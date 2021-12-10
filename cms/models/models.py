# import cProfile, pstats

from peewee import (
    IntegerField,
    TextField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    BooleanField,
    SQL,
    JOIN,
)

from playhouse.sqlite_ext import RowIDField, SearchField, FTSModel

# from playhouse.shortcuts import model_to_dict

from bottle import SimpleTemplate

from .base import BaseModel, OtherModel, db_context, Metadata, MetadataModel

from .enums import (
    PublicationStatus,
    QueueObjType,
    TemplateType,
    TemplatePublishingMode,
    QueueStatus,
    editor_button_colors,
    UserPermission,
)
from cms.settings import APP_URL, APP_DIR
from cms.db import db
from cms.models.utils import (
    create_basename,
    next_month,
    date_to_str,
    unsafe,
    previous_month,
    hash_password,
    tagstrip,
)
from cms.errors import UserNotLoggedIn, MissingFileInfo
from cms import settings

from itertools import product
from time import sleep, perf_counter as clock

import datetime
import os
import pathlib
import sys
import shutil
import functools
import regex as re
import random
import subprocess
import traceback
import json
import imp
import zipfile
import io
import gc


class TemplateError(Exception):
    """
    Exception used for errors in a CMS template.
    """

    def __init__(self, message: str, tpl: "SpecialTemplate", lineno: int):
        self.tpl = tpl
        self.message = message
        self.lineno = lineno
        super().__init__(message)

    def __str__(self):
        try:
            l = ("\n" + unsafe(self.tpl.template_obj.text) + "\n").split("\n")[
                self.lineno
            ]
        except Exception as e:
            l = unsafe(self.tpl.template_obj.text)
        return f"Template: {self.tpl.template_obj.title}\nLine: {self.lineno}\n>>> {l}\n{self.message}"


class SpecialTemplate(SimpleTemplate):
    """
    Modified version of the Bottle SimpleTemplate. Modifications include special keywords and caching of compiled templates in a blog's template set.
    """

    localcache = {}
    ssi = {}

    insert_re = re.compile(r"""^\s*?%\s*?insert\s*?\(['"](.*?)['"]\)""", re.MULTILINE)

    def __init__(self, template: "Template", *a, **ka):
        self.template_obj = template
        self.theme = self.template_obj.theme

        ka["source"] = self.template_obj.text

        # Replacing `insert`s wholesale does not seem to provide
        # any performance benefit.

        # text = self.template_obj.text
        # while True:
        #     found = False
        #     for match in self.insert_re.finditer(text):
        #         found = True
        #         tpl = Template.get(theme=self.theme, title=match[1]).text
        #         text = text.replace(match[0], tpl, 1)
        #     if not found:
        #         break
        # ka["source"] = text

        super().__init__(*a, **ka)

    def _insert(self, _env, _name=None, **kwargs):
        try:
            template_to_insert = self.localcache[(self.theme.id, _name)]
        except KeyError:
            template_to_insert = Template.get(theme=self.theme, title=_name)._cached()
            self.localcache[(self.theme.id, _name)] = template_to_insert
        env = _env.copy()
        env.update(kwargs)
        return template_to_insert.execute(env["_stdout"], env)

    def _load(self, _env, _name=None, **kwargs):
        try:
            template_to_insert = self.localcache[(self.theme.id, _name)]
        except KeyError:
            template_to_insert = Template.get(theme=self.theme, title=_name)
            if template_to_insert.text.startswith("#!"):
                code = template_to_insert.text
                module = imp.new_module(_name)
                exec(code, module.__dict__)
                template_to_insert = module
            else:
                template_to_insert = template_to_insert._cached().execute([], {})
            self.localcache[(self.theme.id, _name)] = template_to_insert
        return template_to_insert

    def _ssi(self, _env, _name=None, **kwargs):
        try:
            ssi_to_insert = self.ssi[(self.theme.id, _name)]
        except KeyError:
            ssi_to_insert = Template.get(theme=self.theme, title=_name).ssi()
            self.ssi[(self.theme.id, _name)] = ssi_to_insert
        _env["_stdout"].append(ssi_to_insert)
        return _env

    def execute(self, _stdout, kwargs):
        env = self.defaults.copy()
        env.update(kwargs)
        env.update(
            {
                "_stdout": _stdout,
                "_printlist": _stdout.extend,
                "insert": functools.partial(self._insert, env),
                "ssi": functools.partial(self._ssi, env),
                "include": functools.partial(self._include, env),
                "rebase": functools.partial(self._rebase, env),
                "_rebase": None,
                "_str": self._str,
                "_escape": self._escape,
                "get": env.get,
                "setdefault": env.setdefault,
                "defined": env.__contains__,
                "load": functools.partial(self._load, env),
            }
        )
        try:
            eval(self.co, env)
        except Exception as e:
            lasterr = e.__traceback__.tb_next
            # print (self.co.__dir__())
            # print (e.__traceback__.tb_next.tb_frame.f_code.co_filename)
            raise TemplateError(e, self, lasterr.tb_lineno)
        if env.get("_rebase"):
            subtpl, rargs = env.pop("_rebase")
            rargs["base"] = "".join(_stdout)  # copy stdout
            del _stdout[:]  # clear stdout
            return self._include(env, subtpl, **rargs)
        return env


class PubStatusField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return PublicationStatus(value)


class TemplateTypeField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return TemplateType(value)


class PublishingModeField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return TemplatePublishingMode(value)


class QueueObjTypeField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return QueueObjType(value)


class QueueStatusField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return None if value is None else QueueStatus(value)


class PermissionField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return UserPermission(value)


class Log(BaseModel):
    date = DateTimeField(default=datetime.datetime.utcnow, index=True)
    level = IntegerField()
    message = TextField()


class User(BaseModel):
    name = CharField(index=True, null=False)
    basename = CharField(null=False, unique=True)
    email = CharField(index=True, null=False, unique=True)
    password = CharField(null=False)
    last_login = DateTimeField(null=True)
    logout_nonce = CharField(max_length=64, null=True, default=None)

    @property
    def title(self):
        return self.name

    def change_name(self, new_name: str):
        old_name = self.name
        self.name = new_name
        if new_name != old_name:
            self.save(basename=False)

    def change_email(self, new_email: str):
        old_email = self.email
        self.email = new_email
        if new_email != old_email:
            try:
                other_user = User.get(email=new_email)
            except User.DoesNotExist:
                self.save(basename=False)
            else:
                raise Exception(
                    f"Email {new_email} already exists. User account emails must be unique."
                )

    def change_password(self, new_password: str):
        # TODO: password complexity
        old_password = self.password
        new_password = hash_password(str(new_password)).hex()
        if new_password != old_password:
            self.password = new_password
            self.save(basename=False)

    def add_permission(self, blog: "Blog", permission: UserPermission):
        p, created = Permission.get_or_create(
            user=self, blog=blog, permission=permission
        )
        if permission == UserPermission.ADMINISTRATOR:
            p.blog_id = 0
            p.save()

    def remove_permission(self, blog: "Blog", permission: UserPermission):
        Permission.delete().where(
            Permission.user == self,
            Permission.blog == blog,
            Permission.permission == permission,
        ).execute()

    @property
    def permissions(self):
        return set((p.blog_id, p.permission) for p in self.user_permissions)

    @property
    def permissions_detail(self):
        return set(
            (p.blog if p.blog_id != 0 else System, p) for p in self.user_permissions
        )

    # Listing methods
    @classmethod
    def listing_columns(cls):
        return "ID", "Name", "Email"

    def listing(self):
        return self.id, self.manage_link_html, self.email

    @property
    def manage_link(self):
        return f"{APP_URL}/user/{self.id}"

    @property
    def title_for_unsafe_display(self):
        return f"<b>{unsafe(self.name)}</b>"

    def save(self, basename=True):
        if basename:
            if self.basename:
                base_to_use = self.basename
            else:
                base_to_use = self.name
            ext = ""
            ext_counter = 0
            while True:
                base = create_basename(f"{base_to_use}{ext}")
                try:
                    User.get(User.basename == base)
                except User.DoesNotExist:
                    break
                else:
                    ext_counter += 1
                    ext = f"-{ext_counter}"

            self.basename = base
        return super().save()

    def create_token(self):
        token = LoginTokens.create(user=self, token=os.urandom(32).hex())
        return token.token

    @classmethod
    def get_by_token(cls, token: str):
        try:
            return LoginTokens.get(LoginTokens.token == token).user
        except LoginTokens.DoesNotExist:
            raise UserNotLoggedIn()

    def clear_token(self, token: str):
        t = self.tokens.where(LoginTokens.token == token).get()
        t.delete_instance()


class LoginTokens(BaseModel):
    user = ForeignKeyField(User, index=True, backref="tokens")
    token = CharField(max_length=128, null=True, default=None)
    date_created = DateTimeField(default=datetime.datetime.utcnow)

    @classmethod
    def clear_expired(cls):
        expired = (
            cls.delete()
            .where(
                cls.date_created
                < datetime.datetime.utcnow() - datetime.timedelta(days=60)
            )
            .execute()
        )


class Theme(BaseModel):
    title = TextField(null=False)
    description = TextField(null=False)
    blog_id = IntegerField(null=True)
    source_dir = TextField(null=False)
    source_theme = IntegerField(null=True)

    @property
    def safe_title(self):
        return create_basename(self.title)

    def as_archive(self):

        mem = io.BytesIO()
        archive = zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED)

        metadata = {}
        metadata["title"] = self.title
        metadata["description"] = self.description
        templates = metadata["templates"] = {}

        template: Template

        for idx, template in enumerate(self.templates):
            template_name = f"{idx}_{create_basename(template.title)}.tpl"
            current_template = templates[template_name] = {}
            current_template["id"] = idx
            current_template["legacy_id"] = template.id
            current_template["title"] = template.title
            current_template["type"] = template.template_type.value
            current_template["publishing_mode"] = template.publishing_mode.value
            current_template["mappings"] = [
                [mapping.mapping, mapping.default_for_archive]
                for mapping in template.mappings
            ]
            # current_template["text"] = template.text
            archive.writestr(f"templates/{template_name}", template.text)

        archive.writestr("metadata.json", json.dumps(metadata, indent=4))

        archive.close()

        return mem.getvalue()

    def save_copy(self):
        now = datetime.datetime.now()
        return self.make_instance(
            None, f"{self.title} (Rev. {now.year}/{now.month}/{now.day})",
        )

    @property
    def templates(self):
        return Template.select().where(Template.theme == self)

    @property
    def manage_link(self):
        return f"{APP_URL}/theme/{self.id}"

    # Listing methods
    @classmethod
    def listing_columns(cls, **ka):
        return "ID", "Blog", "Title", "Description", ""

    def listing(self, blog_context=None):
        if self.blog_id:
            blog = Blog.get(self.blog_id).manage_link_html
        else:
            blog = "[System]"
        return (
            self.id,
            blog,
            self.manage_link_html,
            self.description,
            f'<a class="badge badge-success" href="apply-theme/{self.id}">Apply</a>'
            if blog_context
            else "",
        )

    theme_data_base_path = pathlib.Path(APP_DIR, "setup", "themes")

    def remove_theme(self):
        with db.atomic():
            for template in self.templates:
                template.delete_instance(recursive=True)
            self.delete_instance()

    def make_instance(self, blog: "Blog", title=None):
        if title is None:
            title = f"{self.title} (for blog #{self.id})"
        theme_instance = Theme.create(
            title=title,
            description=self.description,
            blog_id=blog.id if blog is not None else None,
            source_dir=self.source_dir,
            source_theme=self.id,
        )
        for template in self.templates:
            new_theme_template = Template.create(
                theme=theme_instance,
                title=template.title,
                text=template.text,
                template_type=template.template_type,
                publishing_mode=template.publishing_mode,
            )
            for mapping in template.mappings:
                TemplateMapping.create(
                    template=new_theme_template,
                    mapping=mapping.mapping,
                    default_for_archive=mapping.default_for_archive,
                )
        return theme_instance

    @classmethod
    def install_theme(cls, theme_name="default_theme"):

        # TODO: move these to sitewide settings

        theme_data_path = pathlib.Path(cls.theme_data_base_path, theme_name)
        theme_metadata_path = pathlib.Path(theme_data_path, "metadata.json")

        with open(theme_metadata_path, encoding="UTF-8") as theme_data_file:
            theme = json.load(theme_data_file)

        with db.atomic():

            new_theme = Theme.create(
                title=theme["title"],
                description=theme["description"],
                source_dir=theme_data_path,
            )

            for k in theme["templates"]:
                template = theme["templates"][k]
                with open(
                    pathlib.Path(theme_data_path, "templates", k), encoding="UTF-8"
                ) as template_file:

                    new_template = Template.create(
                        theme=new_theme,
                        title=template["title"],
                        template_type=TemplateType(template["type"]),
                        publishing_mode=TemplatePublishingMode(
                            template["publishing_mode"]
                        ),
                        text=template_file.read(),
                    )
                    for idx, mapping in enumerate(template["mappings"]):
                        new_template_mapping = TemplateMapping.create(
                            template=new_template,
                            mapping=mapping[0],
                            default_for_archive=mapping[1],
                        )

        return new_theme


class Blog(BaseModel):
    title = TextField(null=False)
    description = TextField(null=True)
    base_url = TextField(null=False)
    base_filepath = TextField(null=False)
    base_filetype = CharField(null=False, default="html")
    indexfile = CharField(null=False, default="index")
    timezone = TextField(null=True, default="UTC")
    media_path = TextField(null=False, default="__media")
    media_upload_path = TextField(null=False, default="$Y")

    mapping_replacements = {
        "$Y": "{date_value.year}",
        "$m": "{date_value.month:02}",
    }

    # def json(self):
    #     blog_dict = model_to_dict(self)
    #     blog_dict["posts"] = [model_to_dict(x, recurse=False) for x in self.posts]
    #     blog_dict["media"] = [model_to_dict(x, recurse=False) for x in self.media]
    #     return json.dumps(blog_dict, default=str)

    # TODO: fts for media?

    def media_search(self, query: str, source=None):
        if source is None:
            source = self.media
        return source.where(
            (
                Media.filename ** (f"%{query}%")
                | Media.filepath ** (f"%{query}%")
                | Media.friendly_name ** (f"%{query}%")
            )
        ).order_by(Media.id.desc())

    def search(self, query: str, source=None):
        if source is None:
            source = self.posts
        return source.where(
            (Post.text.contains(query)) | (Post.title ** (f"%{query}%"))
        ).order_by(Post.id.desc())

    def delete_instance(self, *a, **ka):
        PostIndex.delete().where(
            PostIndex.rowid << Post.select(Post.id).where(Post.blog == self)
        ).execute()
        self.theme.delete_instance(recursive=True)
        super().delete_instance(*a, **ka)

    # Fetch methods

    @property
    def queue_items(self):
        return Queue.select().where(Queue.blog == self).order_by(Queue.priority.desc())

    @property
    def theme(self) -> Theme:
        return Theme.get(Theme.blog_id == self.id)

    @property
    def posts(self):
        return Post.select().where(Post.blog == self)

    @property
    def published_posts(self):
        return self.posts.where(Post.status == PublicationStatus.PUBLISHED)

    @property
    def templates(self):
        return Template.select().where(Template.theme == self.theme)

    @property
    def archive_templates(self):
        return self.templates.where(Template.template_type == TemplateType.ARCHIVE)

    @property
    def post_templates(self):
        return self.templates.where(Template.template_type == TemplateType.POST)

    @property
    def index_templates(self):
        return self.templates.where(Template.template_type == TemplateType.INDEX)

    @property
    def ssi_templates(self):
        return self.templates.where(Template.template_type == TemplateType.SSI)

    @property
    def media_templates(self):
        return self.templates.where(Template.template_type == TemplateType.MEDIA)

    @property
    def tags(self):
        return Tag.select().where(Tag.blog == self)

    @property
    def categories(self):
        return Category.select().where(Category.blog == self)

    @property
    def default_category(self):
        return self.categories.where(Category.default == True).get()

    @property
    def media(self):
        return Media.select().where(Media.blog == self)

    @property
    def computed_media_upload_path(self):
        date_value = datetime.datetime.utcnow()
        path = self.media_upload_path
        for token, replacement in self.mapping_replacements.items():
            path = path.replace(token, replacement.format(date_value=date_value))
        return path

    @property
    def base_media_directory(self):
        return pathlib.Path(self.base_filepath, self.media_path)

    @property
    def media_upload_directory(self):
        return pathlib.Path(self.base_media_directory, self.computed_media_upload_path)

    # Listing methods
    @classmethod
    def listing_columns(cls):
        return "ID", "Title", "Description"

    def listing(self):
        return self.id, self.manage_link_html, unsafe(self.description)

    # Link methods for management

    @property
    def base_link(self):
        return f"{APP_URL}/blog"

    @property
    def manage_link(self):
        return f"{self.base_link}/{self.id}"

    @property
    def republish_link(self):
        return f"{self.manage_link}/republish"

    @property
    def create_post_link(self):
        return f"{self.manage_link}/new-post"

    @property
    def posts_search_link(self):
        return f"{self.manage_link}/search"

    @property
    def manage_categories_link(self):
        return f"{self.manage_link}/categories"

    @property
    def create_category_link(self):
        return f"{self.manage_link}/new-category"

    @property
    def queue_manage_link(self):
        return f"{self.manage_link}/queue"

    @property
    def posts_link(self):
        return f"{self.manage_link}/posts"

    @property
    def templates_link(self):
        return f"{self.manage_link}/templates"

    @property
    def manage_media_link(self):
        return f"{self.manage_link}/media"

    @property
    def media_search_link(self):
        return f"{self.manage_link}/media-search"

    @property
    def upload_link(self):
        return f"{self.manage_link}/upload"

    @property
    def upload_advanced_link(self):
        return f"{self.manage_link}/media-upload"

    @property
    def manage_tags_link(self):
        return f"{self.manage_link}/tags"

    @property
    def search_tags_link(self):
        return f"{self.manage_tags_link}/search"

    @property
    def tag_fetch_link(self):
        return f"{self.manage_link}/tag-fetch"

    create_link = f"{APP_URL}/new-blog"

    # Link methods for publishing

    @property
    def permalink(self):
        return f"{self.base_url}"

    @property
    def media_permalink(self):
        return f"{self.permalink}/{self.media_path}"

    @property
    def ssi_filepath(self):
        return f"_include"

    @property
    def ssi_url(self):
        return "//_include"

    # Utility methods

    def create_category(self, title: str, description="", basename=None):
        new_category = Category.create(
            title=title, description=description, blog=self, basename=basename
        )
        base_to_use = new_category.basename if basename else new_category.title
        ext = ""
        ext_counter = 0
        while True:
            base = create_basename(f"{base_to_use}{ext}")
            try:
                Category.get(Category.basename == base)
            except Category.DoesNotExist:
                break
            else:
                ext_counter += 1
                ext = f"-{ext_counter}"
        new_category.basename = base
        new_category.save()

    def add_tag(self, tag_title: str) -> "Tag":
        new_tag = Tag(title=tag_title, blog=self)
        new_tag.verify_basename()
        new_tag.save()
        return new_tag

    def remove_theme(self):
        try:
            self.theme.remove_theme()
        except Theme.DoesNotExist:
            pass

    def build_index_fileinfos(self):
        FileInfo.build_index_fileinfos_for_blog(self)

    def apply_theme(self, theme: "Theme"):

        with db.atomic():
            self.remove_theme()
            theme.make_instance(self)
            self.build_index_fileinfos()

        for _ in ("assets", "static"):
            input_path = pathlib.Path(theme.source_dir, _)
            if input_path.exists():
                output_path = pathlib.Path(self.base_filepath, f"_{_}")
                if output_path.exists():
                    shutil.rmtree(output_path)
                shutil.copytree(input_path, output_path)

    def queue_indexes(self):
        total = 0
        for m in (self.ssi_templates, self.index_templates):
            for t in m:
                for f in t.fileinfos:
                    _, count = f.enqueue()
                    total += count
        return total

    def queue_jobs(self):
        return Queue.select().where(
            Queue.blog == self, Queue.obj_type != QueueObjType.CONTROL
        )

    @classmethod
    def scheduled_posts(cls):
        return Post.select().where(
            Post.status == PublicationStatus.SCHEDULED,
            Post.date_published <= datetime.datetime.utcnow(),
        )

    @classmethod
    def queue_scheduled_posts(cls):
        for post in cls.scheduled_posts():
            post.status = PublicationStatus.PUBLISHED
            post.save()
            post.enqueue()

    def queue_badge(self):
        # TODO: move to System object
        style = "success"
        queue_count = self.queue_items.count()
        if Queue.is_locked(self):
            style = "warning"
        else:
            if queue_count:
                style = "primary"
        if Queue.failures(self):
            style = "danger"
        return (
            f'<span id="queue-badge" class="badge badge-{style}">{queue_count}</span>'
        )


class Category(BaseModel):
    title = TextField(null=False)
    description = TextField(null=True)
    basename = TextField(null=False)
    blog = ForeignKeyField(Blog, index=True)
    default = BooleanField(default=True)

    # Fetch methods

    @property
    def posts(self):

        cat_posts = PostCategory.select(PostCategory.post).where(
            PostCategory.category == self
        )

        cp2 = self.blog.posts.where(Post.id << cat_posts)

        return cp2

    @property
    def published_posts(self):
        return self.posts.where(Post.status == PublicationStatus.PUBLISHED)

    # Link methods

    @property
    def manage_link_html(self):
        return f'<b><a href="{self.edit_link}">{self.title}</a></b>'

    @property
    def manage_link(self):
        return f"{self.blog.manage_link}/category/{self.id}"

    @property
    def in_posts_link(self):
        return f"{self.manage_link}/posts"

    @property
    def edit_link(self):
        return f"{self.manage_link}/edit"

    @property
    def delete_link(self):
        return f"{self.manage_link}/delete"

    @property
    def permalink(self):
        # TODO: eventually this will be derived from the default category mapping
        return f"{self.blog.permalink}/{self.basename}"

    # Listing methods
    @classmethod
    def listing_columns(cls):
        return (
            "ID",
            "",
            "Title",
            "Posts",
        )

    def listing(self):
        return (
            self.id,
            '<span class="badge badge-success">Default</span>'
            if self.blog.default_category == self
            else "",
            self.manage_link_html,
            f'<a href="{self.in_posts_link}">{self.posts.count()}</a>',
        )


class Permission(BaseModel):
    user = ForeignKeyField(User, index=True, backref="user_permissions")
    blog = ForeignKeyField(Blog, index=True)
    permission = PermissionField(default=UserPermission.AUTHOR)


class Post(BaseModel):
    title = TextField(null=False)
    basename = TextField(null=False)
    excerpt_ = TextField(null=True)
    blog = ForeignKeyField(Blog, index=True)
    author = ForeignKeyField(User, index=True)
    text = TextField(null=True)
    is_dirty = BooleanField(null=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow, index=True)
    date_last_modified = DateTimeField(default=datetime.datetime.utcnow, index=True)
    date_published = DateTimeField(default=datetime.datetime.utcnow, index=True)
    status = PubStatusField(default=PublicationStatus.DRAFT, index=True)
    open_for_editing_by = ForeignKeyField(User, null=True)

    permalink_cache = {}

    excerpt_re = re.compile("<p>(.*?)</p>")

    @property
    def date_created_str(self):
        return date_to_str(self.date_created)

    @property
    def date_published_str(self):
        return date_to_str(self.date_published)

    @property
    def date_last_modified_str(self):
        return date_to_str(self.date_last_modified)

    @property
    def tags_list(self):
        try:
            return self._tags_list
        except:
            self._tags_list = [x.title for x in self.tags]
            return self._tags_list

    def delete_instance(self, *a, **ka):
        with db.atomic():
            self.clear_fileinfos()
            # TODO: delete instance on fileinfo also dequeues
            for f in self.media_:
                f.delete_instance(recursive=True)
            for f in self.categories_:
                f.delete_instance(recursive=True)
            for f in self.tags:
                self.remove_tag(f)
            self.delete_fts_index()

            super().delete_instance(*a, **ka)

    @property
    def body(self):
        try:
            return self._segment
        except AttributeError:
            self._segment = self.text.split("<!-- pagebreak -->")
            return self._segment

    @property
    def excerpt(self):

        if self.excerpt_ and len(self.excerpt_) > 0:
            return self.excerpt_

        if self.text:
            m = self.excerpt_re.match(self.text)
            if m:
                return m[0]
            else:
                return self.text.split("\n")[0]

        return ""

    @classmethod
    def create(cls, *a, **ka):
        category = ka.pop("category", None)
        no_category = ka.pop("no_category", False)
        self = super().create(*a, **ka)
        if no_category is False:
            if category is None:
                category = self.blog.default_category
            PostCategory.create(post=self, category=category, is_primary=True)
        self.update_index()
        return self

    def update_index(self):
        self.delete_fts_index()
        PostIndex.update(title=self.title, text=self.text).where(
            PostIndex.rowid == self.id
        ).execute()

    def delete_fts_index(self):
        PostIndex.delete().where(PostIndex.rowid == self.id).execute()

    def create_basename(self):
        if self.basename:
            base_to_use = self.basename
        else:
            base_to_use = self.title if self.title else "untitled"

        ext = ""
        ext_counter = 0
        base = create_basename(base_to_use)

        while True:
            try:
                Post.get(Post.basename == base, Post.blog == self.blog)
            except Post.DoesNotExist:
                break
            else:
                ext_counter += 1
                ext = f"-{ext_counter}"
                base = create_basename(f"{base_to_use}{ext}")

        return base

    # Fetch methods

    @property
    def permalink_fileinfo(self):

        mappings_for_blog_post_template = TemplateMapping.select(
            TemplateMapping.id
        ).where(
            TemplateMapping.template << self.blog.post_templates,
            TemplateMapping.default_for_archive == True,
        )

        try:
            query = self.fileinfos.where(
                FileInfo.templatemapping << mappings_for_blog_post_template
            ).get()

        except FileInfo.DoesNotExist as e:
            raise MissingFileInfo(e)

        return query

    @property
    def preview_filepath(self):
        return self.permalink_fileinfo.preview_filepath

    @property
    def permalink_filepath(self):

        try:
            return Post.permalink_cache[self.id]
        except KeyError:
            pass

        result = self.permalink_fileinfo

        Post.permalink_cache[self.id] = result.filepath
        return result.filepath

    @property
    def permalink(self):
        if not self.id:
            return ""
        permalink = f"{self.blog.permalink}/{self.permalink_filepath}"
        return permalink

    @property
    def media_(self):
        return MediaAssociation.select(MediaAssociation.media).where(
            MediaAssociation.post == self
        )

    @property
    def media(self):
        return Media.select().where(Media.id << self.media_)

    @property
    def primary_category(self):
        return self.categories_.where(PostCategory.is_primary == True).get().category

    @property
    def categories_(self):
        return PostCategory.select(PostCategory.category).where(
            PostCategory.post == self
        )

    @property
    def categories(self):
        c1 = self.categories_.order_by(Category.default.desc(), Category.title.asc())
        return Category.select().where(Category.id << self.categories_)

    @property
    def subcategories(self):
        return self.categories.where(Category.id != self.primary_category.id)

    @property
    def fileinfo_mappings(self):
        return FileInfoMapping.select(FileInfoMapping.fileinfo).where(
            FileInfoMapping.post == self
        )

    @property
    def fileinfos(self):
        return FileInfo.select().where(FileInfo.id << self.fileinfo_mappings)

    @property
    def tags(self):
        tags_assoc = TagAssociation.select(TagAssociation.tag).where(
            TagAssociation.post == self
        )
        tags = Tag.select().where(Tag.id << tags_assoc).order_by(Tag.title.asc())
        return tags

    @property
    def tags_public(self):
        return self.tags.where(~Tag.title ** ("@%"))

    @property
    def permalink_idx(self):
        return self.permalink.rsplit(
            f"/{self.blog.indexfile}.{self.blog.base_filetype}", 1
        )[0]

    # Listing methods
    @classmethod
    def listing_columns(cls):
        return "ID", "", "Status", "Title", "Open by", "Author", "Category", "Pub Date"
        # return "ID", "", "Status", "Title", "Author", "Category", "Pub Date"

    def listing(self):

        return (
            self.id,
            f'<a target="_blank" href="{self.live_link}"><span class="badge badge-primary">Link</span></a>'
            if self.status == PublicationStatus.PUBLISHED
            else "",
            self.status_txt,
            self.manage_link_html,
            "" if self.open_for_editing_by is None else self.open_for_editing_by.name,
            self.author.manage_link_html,
            self.primary_category.manage_link_html,
            self.date_published_str,
            # date_to_str(self.date_published),
        )

    # Link methods

    @property
    def base_link(self):
        return f"{self.blog.manage_link}/post/{self.id}"

    @property
    def manage_link(self):
        return f"{self.base_link}/edit"

    @property
    def live_link(self):
        return f"{self.base_link}/live"

    @property
    def manage_link_html(self):
        return (
            f'<a class="font-weight-bold" href="{self.manage_link}">{unsafe(self.title)}</a>'
            if self.title
            else f'<a class="text-muted font-weight-bold" href="{self.manage_link}">[<i>Untitled</i>]</a><br><small>{tagstrip(self.text[:50])}...</small>'
        )

    # TODO: move this to Blog
    @classmethod
    def create_link(cls, blog: Blog):
        return f"{blog.manage_link}/new-post"

    @property
    def copy_link(self):
        return f"{self.base_link}/copy"

    @property
    def delete_link(self):
        return f"{self.base_link}/delete"

    @property
    def upload_link(self):
        return f"{self.base_link}/upload"

    @property
    def media_link(self):
        return f"{self.base_link}/media"

    @property
    def media_insert_link(self):
        return f"{self.base_link}/media-insert"

    @property
    def media_templates_link(self):
        return f"{self.base_link}/media-templates"

    @property
    def media_render_link(self):
        return f"{self.base_link}/media-render"

    @property
    def preview_link(self):
        return f"{self.base_link}/preview"

    @property
    def add_tag_link(self):
        return f"{self.base_link}/add-tag"

    @property
    def remove_tag_link(self):
        return f"{self.base_link}/remove-tag"

    @property
    def add_metadata_link(self):
        return f"{self.base_link}/add-metadata"

    @property
    def remove_metadata_link(self):
        return f"{self.base_link}/remove-metadata"

    # Text methods

    @property
    def status_txt(self):
        return f'<span class="badge badge-{editor_button_colors[self.status]}">{PublicationStatus.txt[self.status]}</span>'

    # Major methods

    def add_tag(self, tag_to_add):
        save_tag = TagAssociation.create(tag=tag_to_add, post=self)
        return save_tag

    def remove_tag(self, tag_to_remove):
        try:
            delete_tag = TagAssociation.get(tag=tag_to_remove, post=self)
        except TagAssociation.DoesNotExist:
            pass
        else:
            delete_tag.delete_instance()

    def save(self, *a, **ka):
        fi: FileInfo
        for fi in self.fileinfos:
            fi.clear_preview_file()
        return super().save(*a, **ka)

    def enqueue(self, neighbors=True, indices=True):
        """
        Push this post and all its related archives, and the site indexes, to the queue.
        """

        blog: Blog = self.blog
        fileinfo: FileInfo

        total = 0

        for fileinfo in self.fileinfos:
            _, count = fileinfo.enqueue()
            total += count

        if neighbors:
            total += self.queue_neighbors()

        if indices:
            total += blog.queue_indexes()

        return total

    def dequeue_post_archives(self):
        """
        Remove all post archive jobs from queue for this post.
        Affects only post archives, not dates/categories/tags.
        """

        with db.atomic():
            for fileinfo in self.fileinfos:
                if fileinfo.template.template_type == TemplateType.POST:
                    fileinfo.dequeue()

    def queue_neighbors(self):
        """
        Push next and previous posts in all categories to the queue as well.
        """

        neighbors = []

        for groups in (
            [self.blog],
            [_ for _ in self.categories],
            [_ for _ in self.tags],
        ):

            for group in groups:

                try:
                    neighbors.append(
                        group.published_posts.where(
                            (Post.date_published > self.date_published)
                            | (
                                (
                                    (Post.date_published == self.date_published)
                                    & (Post.id > self.id)
                                )
                            )
                        )
                        .order_by(Post.date_published.asc(), Post.id.asc())
                        .limit(1).get())

                except:
                    pass

                try:
                    neighbors.append(
                        group.published_posts.where(
                            (Post.date_published < self.date_published)
                            | (
                                (
                                    (Post.date_published == self.date_published)
                                    & (Post.id < self.id)
                                )
                            )
                        )
                        .order_by(Post.date_published.desc(), Post.id.desc())
                        .limit(1).get())
                except:
                    pass

        total = 0

        for p in neighbors:
            total += p.enqueue(neighbors=False, indices=False)

        return total

    def unpublish(self):
        """
        Set post to draft mode, delete any existing on-disk files for its post archive, and queue neighbors for republishing.
        """
        Post.permalink_cache.pop(self.id)

        total = 0

        with db.atomic():

            self.status = PublicationStatus.DRAFT
            self.save()

            # TODO: more efficient way to do this?

            unique_path = f"{self.blog.id},{self.permalink_filepath}"
            permalink_fileinfo = FileInfo.get(unique_path=unique_path)
            Queue.add_delete_fileinfo_job(permalink_fileinfo, self.blog)

            total += self.blog.queue_indexes()
            total += self.queue_neighbors()

        return total

    def clear_fileinfos(self):
        with db.atomic():
            # first, dequeue any fileinfos that might be deleted
            fis = self.fileinfos.select(FileInfo.id)
            Queue.delete().where(Queue.fileinfo << fis).execute()

            f: FileInfo
            FileInfoMapping.delete().where(FileInfoMapping.post == self).execute()
            for f in self.fileinfos:
                if f.template.type == TemplateType.POST:
                    f.delete_instance(recursive=True)

        try:
            Post.permalink_cache.pop(self.id)
        except KeyError:
            pass

        Template.clear_cache()

    def build_fileinfos(self):
        with db.atomic():
            FileInfo.build_archive_fileinfos_from_posts([self], self.blog)

    def queue_erase_post_archive_files(self):
        for fileinfo in self.fileinfos:
            if fileinfo.template.template_type == TemplateType.POST:
                Queue.add_delete_file_job(fileinfo.filepath, self.blog)

    def set_primary_category(self, new_category):
        primary = PostCategory.get(post=self, is_primary=True)
        primary.category = new_category
        primary.save()

    def add_subcategory(self, subcategory: Category):
        try:
            cat_to_add = PostCategory.get(post=self, category=subcategory)
        except PostCategory.DoesNotExist:
            PostCategory.create(post=self, category=subcategory)
        else:
            pass

    def remove_subcategory(self, subcategory: Category):
        try:
            cat_to_remove = PostCategory.get(post=self, category=subcategory)
        except PostCategory.DoesNotExist:
            pass
        else:
            cat_to_remove.delete_instance()

    def clear_subcategories(self):
        for subcat in self.categories_.where(PostCategory.is_primary == True):
            subcat.delete_instance()


class PostRevision(Post, OtherModel):
    pass


class PostIndex(FTSModel, OtherModel):
    rowid = RowIDField()
    text = SearchField()
    title = SearchField()

    class Meta:
        database = db
        options = {"content": Post}


class PostCategory(BaseModel):
    post = ForeignKeyField(Post, index=True)
    category = ForeignKeyField(Category, index=True)
    is_primary = BooleanField(default=True)


class Media(BaseModel):
    filename = TextField(null=False)
    filepath = TextField(null=False)
    date_created = DateTimeField(default=datetime.datetime.utcnow, index=True)
    date_last_modified = DateTimeField(default=datetime.datetime.utcnow, index=True)
    friendly_name = TextField(null=True)
    user = ForeignKeyField(User, index=True)
    blog = ForeignKeyField(Blog, index=True)

    @property
    def filesize(self):
        return self.full_filepath.stat().st_size

    @property
    def date_created_str(self):
        return date_to_str(self.date_created)

    @property
    def date_last_modified_str(self):
        return date_to_str(self.date_last_modified)

    @property
    def posts(self):
        return Post.select().where(
            Post.id << self.associations.select(MediaAssociation.post)
        )

    @property
    def full_filepath(self):
        return pathlib.Path(self.blog.base_media_directory, self.filepath)

    @property
    def filename_parts(self):
        return self.filename.rsplit(".", 1)

    @property
    def url(self):
        return f"{self.blog.media_permalink}/{self.filepath}"

    @property
    def relative_url(self):
        return f"/{self.blog.media_path}/{self.filepath}"

    @property
    def image_link_html(self, styling=""):
        return f'<img class="media-thumbnail img-fluid" src="{self.blog.media_permalink}/{self.filepath}"{styling}>'

    @property
    def base_link(self):
        return f"{self.blog.manage_media_link}/{self.id}"

    @property
    def manage_link(self):
        return f"{self.base_link}/edit"

    @property
    def delete_link(self):
        return f"{self.base_link}/delete"

    @property
    def add_metadata_link(self):
        return f"{self.base_link}/add-metadata"

    @property
    def remove_metadata_link(self):
        return f"{self.base_link}/remove-metadata"

    @property
    def used_in_link(self):
        return f"{self.base_link}/in"

    @property
    def manage_link_html(self):
        return f'<a target="_blank" href="{self.manage_link}"><b>{self.image_link_html}</b></a>'

    @property
    def title_for_listing(self):
        return (
            f'<a target="_blank" href="{self.manage_link}"><b>{self.filename}</b></a>'
        )

    # Listing methods
    @classmethod
    def listing_columns(cls):
        return "ID", "Image", "Title", "Description"

    def listing(self):
        return (
            self.id,
            self.manage_link_html,
            self.title_for_listing,
            unsafe(self.friendly_name),
        )

    def delete_file(self):
        if self.full_filepath.exists():
            os.remove(str(self.full_filepath))

    def delete_instance(self, *a, **ka):
        for f in self.associations:
            f.delete_instance()
        self.delete_file()
        super().delete_instance(*a, **ka)


class MediaAssociation(BaseModel):
    media = ForeignKeyField(Media, index=True, backref="associations")
    post = ForeignKeyField(Post, null=True, index=True)

    # we may want to move user/blog here
    # so that Media objects can be used by themes?


class Tag(BaseModel):
    title = TextField(null=False, index=True)
    blog = ForeignKeyField(Blog, index=True,)
    is_hidden = BooleanField(default=False)
    basename = TextField(null=False)

    @classmethod
    def search(cls, query, source=None):
        if source is None:
            source = Tag.select()
        return source.where(Tag.title ** (f"%{query}%")).order_by(Tag.title.asc())

    # Fetch methods

    @property
    def posts(self):
        t1 = TagAssociation.select(TagAssociation.post).where(
            TagAssociation.tag == self, TagAssociation.post << self.blog.posts
        )
        return self.blog.posts.where(Post.id << t1)

    @property
    def published_posts(self):
        return self.posts.where(Post.status == PublicationStatus.PUBLISHED)

    # We may be able to make this generic
    # for any model that has a title and basename

    def verify_basename(self):
        if self.basename:
            base_to_use = self.basename
        else:
            base_to_use = self.title
        ext = ""
        ext_counter = 0
        while True:
            base = create_basename(f"{base_to_use}{ext}")
            try:
                Tag.get(Tag.basename == base, Tag.blog == self.blog)
            except Tag.DoesNotExist:
                break
            else:
                ext_counter += 1
                ext = f"-{ext_counter}"

        self.basename = base

    @property
    def base_link(self):
        return f"{self.blog.manage_link}/tag/{self.id}"

    @property
    def in_posts_link(self):
        return f"{self.base_link}/posts"

    @property
    def search_posts_link(self):
        return f"{self.in_posts_link}/search"

    @property
    def manage_link(self):
        return f"{self.base_link}/edit"

    @property
    def merge_link(self):
        return f"{self.base_link}/merge"

    @property
    def delete_link(self):
        return f"{self.base_link}/delete"

    # Listing methods

    @classmethod
    def listing_columns(cls):
        return "ID", "Title", "Posts"

    def listing(self):
        return (
            self.id,
            self.manage_link_html,
            f'<a href="{self.in_posts_link}">{self.posts.count()}</a>',
        )

    def delete_instance(self, *a, **ka):
        for f in self.associations:
            f.delete_instance()
        super().delete_instance(*a, **ka)


class TagAssociation(BaseModel):
    tag = ForeignKeyField(Tag, index=True, backref="associations")
    post = ForeignKeyField(Post, null=True, index=True)
    media = ForeignKeyField(Media, null=True, index=True)

    def delete_instance(self, *a, **ka):
        super().delete_instance(*a, **ka)
        try:
            TagAssociation.get(tag=self.tag)
        except TagAssociation.DoesNotExist:
            self.tag.delete_instance()


class Template(BaseModel):
    """
    Contains templates used in a blog theme.
    """

    theme = ForeignKeyField(Theme, null=False, index=True,)
    title = CharField(null=False)
    text = TextField(null=True)
    template_type = TemplateTypeField(null=False, index=True)
    publishing_mode = PublishingModeField(null=False, index=True)

    cache = {}
    dbcache = {}

    # Special properties

    @property
    def blog(self):
        return Blog.get_by_id(self.theme.blog_id)

    @property
    def mappings(self):
        return TemplateMapping.select().where(TemplateMapping.template == self)

    @property
    def default_mapping(self):
        return self.mappings.get()

    @property
    def fileinfos(self):
        return FileInfo.select().where(FileInfo.templatemapping << self.mappings)

    # Listing methods

    @classmethod
    def listing_columns(cls):
        return "ID", "Title", "Mapping", ""

    def listing(self):
        return (
            self.id,
            self.manage_link_html,
            "[<i>No mapping for includes</i>]"
            if self.template_type in (TemplateType.INCLUDE, TemplateType.MEDIA)
            else f"<code>{self.default_mapping.mapping}</code>",
            '<span class="badge badge-success">Default for archive</span>'
            if self.mappings.where(TemplateMapping.default_for_archive == True).count()
            else "",
        )

    # Link methods

    @property
    def base_link(self):
        return f"{APP_URL}/blog/{self.blog.id}/template/{self.id}"

    @property
    def manage_link(self):
        return f"{self.base_link}/edit"

    @classmethod
    def create_link(cls, blog: Blog, tab: str):
        return f"{blog.manage_link}/new-template/{tab}"

    @property
    def republish_all_link(self):
        return f"{self.base_link}/republish-all"

    # Special methods

    @classmethod
    def clear_cache(cls):
        cls.cache = {}
        cls.dbcache = {}
        SpecialTemplate.localcache = {}
        SpecialTemplate.ssi = {}
        FileInfo.tags = {}
        FileInfo.categories = {}

    def _cached(self):
        try:
            return Template.cache[self.id]
        except KeyError:
            tpl = SpecialTemplate(self)
            Template.cache[self.id] = tpl
            return tpl

    @classmethod
    def _dbcache(cls, id):
        try:
            return cls.dbcache[id]
        except KeyError:
            tpl = cls.get_by_id(id)
            cls.dbcache[id] = tpl
            return tpl

    def render(self, **ka):
        return self._cached().render(**ka)

    def ssi(self):
        return f'<!--#include virtual="/{self.fileinfos.get().filepath}" -->'

    def dequeue_failed(self):
        Queue.delete().where(
            Queue.fileinfo << self.fileinfos, Queue.status == QueueStatus.FAILED
        ).execute()

    def enqueue(self, manual_ok=False):
        blog: Blog = self.blog
        fileinfo: FileInfo
        total = 0
        for fileinfo in self.fileinfos:
            _, count = fileinfo.enqueue(manual_ok)
            total += count
        return total

    def add_mapping(self, mapping: str):
        return TemplateMapping.create(template=self, mapping=mapping)

    def build_fileinfos(self):
        FileInfo.build_fileinfos(
            None, self.blog, [self], {self.id: [_ for _ in self.mappings]}
        )


class TemplateMapping(BaseModel):
    """
    Describes the file paths where a template will write its files.
    Templates can have multiple mappings.
    """

    template = ForeignKeyField(Template, index=True,)
    mapping = TextField(null=False)
    archive_xref = CharField(max_length=8, null=True)
    date_last_modified = DateTimeField(default=datetime.datetime.utcnow)
    default_for_archive = BooleanField(default=False)

    @property
    def fileinfos(self):
        return FileInfo.select().where(FileInfo.templatemapping == self)

    def dequeue(self):
        Queue.delete().where(Queue.fileinfo << self.fileinfos).execute()

    def clear_fileinfos(self):

        Post.permalink_cache = {}

        with db.atomic():

            FileInfoMapping.delete().where(
                FileInfoMapping.fileinfo << self.fileinfos
            ).execute()

            Context.delete().where(Context.fileinfo << self.fileinfos).execute()

            FileInfo.delete().where(FileInfo.id << self.fileinfos).execute()


class FileInfo(BaseModel):
    """
    A single physical file path created by a template mapping.    
    The `unique_path` field ensures that no two fileinfos in a blog
    will have the same path.
    """

    # recursive will delete FileInfoMapping
    filepath = TextField(null=False, index=True)
    templatemapping = ForeignKeyField(TemplateMapping, index=True,)
    template = ForeignKeyField(Template, index=True)
    blog = ForeignKeyField(Blog, index=True)
    unique_path = TextField(unique=True, index=True, null=False)
    preview_built = BooleanField(default=False)

    map_re = re.compile(r"\$.")

    mapping_replacements = {
        "$A": "{post.author.basename}",
        "$Y": "{post.date_published.year}",
        "$m": "{post.date_published.month:02}",
    }

    filetype_replacements = {
        "$f": "{post.basename}.{post.blog.base_filetype}",
        "$i": "{post.blog.indexfile}.{post.blog.base_filetype}",
        "$b": "{post.basename}",
        "$s": "{post.blog.ssi_filepath}",
    }

    mapping_iterable_replacements = {
        "$C": "{category.basename}",
        "$t": "{tag.basename}",
    }

    all_replacements = {}
    all_replacements.update(mapping_replacements)
    all_replacements.update(filetype_replacements)
    all_replacements.update(mapping_iterable_replacements)

    maps = {}
    maps.update(mapping_replacements)
    maps.update(mapping_iterable_replacements)

    filetypes = filetype_replacements.items()

    priorities = {
        TemplateType.SSI: 9,
        TemplateType.POST: 8,
        TemplateType.INDEX: 7,
        TemplateType.ARCHIVE: 6,
    }

    def delete_instance(self, *a, **ka):
        Context.delete().where(Context.fileinfo == self).execute()
        FileInfoMapping.delete().where(FileInfoMapping.fileinfo == self).execute()
        super().delete_instance(*a, **ka)

    @property
    def priority(self):
        return self.priorities[Template._dbcache(self.template_id).template_type]

    @classmethod
    def make_filepaths(cls, post, mapping_string):

        """
        If the mapping begins with a single or double quote,
        we interpret it as a string to be formatted,
        with a comment afterwards to indicate the mapping order.
        context is then created and used to generate the string

        'tag/{t[0]}/{t[1]}/$i'.format(t=tag.title.split(':',1)) # $t/$i

        """

        tags = {}
        categories = {}
        context = []
        context_stack = []
        format_string = mapping_string
        use_expression = False

        if mapping_string[0] in ("'", '"'):
            use_expression = True
            format_string, mapping_string = mapping_string.split("#", 1)

        for key, replacement in cls.filetypes:
            mapping_string = mapping_string.replace(key, replacement)

        for m in cls.map_re.finditer(mapping_string):
            key = m[0]
            replacement = cls.maps[key]

            mapping_string = mapping_string.replace(key, replacement)
            key = key[-1]
            context.append(key)

            if key == "Y":
                context_stack.append([post.date_published.year])
            elif key == "m":
                context_stack.append([post.date_published.month])
            elif key == "A":
                context_stack.append([post.author_id])

            elif key == "C":
                c_stack = []
                for c in post.categories:
                    c_stack.append(c.id)
                    categories[c.id] = c
                context_stack.append(c_stack)

            elif key == "t":
                t_stack = []
                for t in post.tags:
                    t_stack.append(t.id)
                    tags[t.id] = t
                context_stack.append(t_stack)

        context_str = "".join(context)

        final_stack = []
        data_dict = {"post": post}

        for _ in product(*context_stack):
            data_stack = []
            for data, ctx in zip(_, context):
                if ctx == "t":
                    data_dict["tag"] = tags[data]
                elif ctx == "C":
                    data_dict["category"] = categories[data]
                data_stack.append(data)
            try:
                if use_expression:
                    context_path = format_string
                    for key, replacement in cls.all_replacements.items():
                        if key in context_path:
                            context_path = context_path.replace(
                                key, replacement.format(**data_dict)
                            )
                    context_path = eval(context_path, None, data_dict)
                    # context_path = context_path.format(**data_dict)
                else:
                    context_path = mapping_string.format(**data_dict)
                if context_path == "":
                    continue
                final_stack.append([context_path, data_stack, context_str])
            except IndexError as e:
                raise e

        return final_stack

    @classmethod
    def build_fileinfos(cls, posts, blog, templates, mappings):
        if posts is None:
            posts = [Post(blog=blog)]
        for p in posts:
            for template in templates:
                for mapping in mappings[template.id]:
                    filepaths = cls.make_filepaths(p, mapping.mapping)
                    for filepath, archive_context, context_id in filepaths:
                        fi, created = FileInfo.get_or_create(
                            unique_path=f"{blog.id},{filepath}",
                            defaults={
                                "filepath": filepath,
                                "templatemapping": mapping,
                                "template": template,
                                "blog": blog,
                            },
                        )

                        if created:
                            for idx, context_data in enumerate(archive_context):
                                # print ("FIID", fi.id)
                                Context.create(
                                    fileinfo=fi,
                                    context_type=context_id[idx],
                                    context_id=context_data,
                                    sort=idx,
                                )

                        FileInfoMapping.create(
                            fileinfo=fi, post=p,
                        )

    @classmethod
    def build_archive_fileinfos_from_posts(cls, posts, blog):
        templates = [
            t
            for t in blog.templates.where(
                Template.template_type << (TemplateType.ARCHIVE, TemplateType.POST)
            )
        ]
        mappings = {
            template.id: [m for m in template.mappings] for template in templates
        }
        cls.build_fileinfos(posts, blog, templates, mappings)

    @classmethod
    def build_index_fileinfos_for_blog(cls, blog):
        templates = [
            t
            for t in blog.templates.where(
                Template.template_type << (TemplateType.INDEX, TemplateType.SSI)
            )
        ]
        mappings = {
            template.id: [m for m in template.mappings] for template in templates
        }
        cls.build_fileinfos(None, blog, templates, mappings)

    @property
    def mappings(self):
        return FileInfoMapping.select().where(FileInfoMapping.fileinfo == self)

    @property
    def context(self):
        return (
            Context.select()
            .where(Context.fileinfo == self)
            .order_by(Context.sort.asc())
        )

    @property
    def preview_filepath(self):
        return f"{self.filepath}.preview.{self.blog.base_filetype}"

    def write_preview_file(self):
        # print(self.id)
        self.write_file(True)
        self.update(preview_built=True).where(FileInfo.id == self).execute()

    def clear_preview_file(self):
        p = pathlib.Path(self.blog.base_filepath, self.preview_filepath)
        if p.exists():
            os.remove(str(p))
        self.update(preview_built=False).where(FileInfo.id == self).execute()

    def write_file(self, as_preview=False):
        output_template = self.template
        if output_template.template_type == TemplateType.POST:
            ctx = ArchiveContext(self.mappings.get().post, self.templatemapping)
        else:
            ctx = ArchiveContext(self, self.templatemapping)

        output_text = output_template.render(post=ctx.post, blog=ctx.blog, archive=ctx)
        output_path = pathlib.Path(
            ctx.blog.base_filepath,
            self.preview_filepath if as_preview else self.filepath,
        )
        output_path_parent = output_path.parents[0]

        if not output_path_parent.exists():
            os.makedirs(output_path_parent)

        with open(output_path, "w", encoding="utf8") as f:
            f.write(output_text)

    def remove_file(self):
        output_path = pathlib.Path(self.blog.base_filepath, self.filepath)
        if output_path.exists():
            os.remove(output_path)

    def enqueue(self, manual_ok=False):
        t = Template._dbcache(self.template_id).publishing_mode
        if t == TemplatePublishingMode.QUEUE or (
            manual_ok and t == TemplatePublishingMode.MANUAL
        ):
            return Queue.add_fileinfo_job(self, self.blog)
        return None, 0

    def dequeue(self):
        Queue.delete().where(
            Queue.blog == self.blog,
            Queue.obj_type == QueueObjType.WRITE_FILEINFO,
            Queue.fileinfo == self,
        ).execute()


class FileInfoMapping(BaseModel):
    """
    Describes which fileinfos are used to write all the files associated
    with a given blog post, include template, or index template.
    """

    fileinfo = ForeignKeyField(FileInfo, index=True,)
    post = ForeignKeyField(Post, null=True, index=True,)


class Context(BaseModel):
    """
    Describes the context associated with a given fileinfo/post combination.
    There must only be one set of these for each fileinfo.
    """

    fileinfo = ForeignKeyField(FileInfo, index=True)
    context_type = CharField(max_length=1, index=True)
    context_id = IntegerField(index=True)
    sort = IntegerField()


class Queue(BaseModel):
    obj_type = QueueObjTypeField(null=False, index=True)
    status = QueueStatusField(index=True, default=QueueStatus.WAITING)
    priority = IntegerField(null=False, default=10, index=True)
    blog = ForeignKeyField(Blog, index=True)
    fileinfo = ForeignKeyField(FileInfo, index=True, null=True)
    text_data = TextField(null=True)
    integer_data = IntegerField(null=True)
    failure_data = TextField(null=True)
    date_inserted = DateTimeField(default=datetime.datetime.utcnow)
    date_updated = DateTimeField(default=datetime.datetime.utcnow)

    # profiler = None

    worker = None
    state = None

    # Listing methods

    @property
    def date_inserted_str(self):
        return date_to_str(self.date_inserted)

    @classmethod
    def listing_columns(cls):
        return "ID", "Type", "Fileinfo", "Template", "Status", "Priority", "Date"

    def listing(self):

        return (
            self.id,
            QueueObjType.txt[self.obj_type],
            self.fileinfo.filepath if self.fileinfo else "",
            self.fileinfo.template.title if self.fileinfo else "",
            ""
            if self.status is None
            else f'<a href="{self.manage_item_link}">{QueueStatus.txt[self.status]}</a>',
            self.priority,
            self.date_inserted_str
            # date_to_str(self.date_inserted),
        )

    @property
    def manage_item_link(self):
        return f"{self.blog.manage_link}/queue-item/{self.id}"

    @classmethod
    def failures(cls, blog=None):
        failures = cls.select().where(cls.status == QueueStatus.FAILED)
        if blog is not None:
            failures = failures.where(cls.blog == blog)
        return failures

    @classmethod
    def add_fileinfo_job(cls, fileinfo: FileInfo, blog: Blog):
        now = datetime.datetime.utcnow()
        return cls.get_or_create(
            obj_type=QueueObjType.WRITE_FILEINFO,
            fileinfo=fileinfo,
            defaults={
                "priority": fileinfo.priority,
                "blog": blog,
                "date_inserted": now,
                "date_updated": now,
            },
        )

    @classmethod
    def add_delete_fileinfo_job(cls, fileinfo: FileInfo, blog: Blog):
        with db.atomic():
            try:
                existing_job = cls.get(
                    obj_type=QueueObjType.DEL_FILEINFO, fileinfo=fileinfo
                )
            except Queue.DoesNotExist:
                now = datetime.datetime.utcnow()
                new_job = cls.create(
                    obj_type=QueueObjType.DEL_FILEINFO,
                    priority=0,
                    blog=blog,
                    fileinfo=fileinfo,
                    date_inserted=now,
                    date_updated=now,
                )
                return new_job
            else:
                return existing_job

    @classmethod
    def add_delete_file_job(cls, file_path: str, blog: Blog):
        with db.atomic():
            try:
                existing_job = cls.get(
                    obj_type=QueueObjType.DEL_FILE, text_data=file_path, blog=blog
                )
            except Queue.DoesNotExist:
                now = datetime.datetime.utcnow()
                new_job = cls.create(
                    obj_type=QueueObjType.DEL_FILE,
                    text_data=file_path,
                    priority=11,
                    blog=blog,
                    date_inserted=now,
                    date_updated=now,
                )
                return new_job
            return existing_job

    def lock(self):
        self.status = QueueStatus.RUNNING
        self.save()

    def unlock(self):
        self.status = QueueStatus.WAITING
        self.save()

    @classmethod
    def stop(cls, blog):
        p = cls.control_jobs(blog)
        if p:
            p.status = QueueStatus.STOPPED
            p.save()

    @classmethod
    def restart(cls, blog):
        p = cls.control_jobs(blog)
        if p:
            p.status = QueueStatus.WAITING
            p.save()
        cls.start(force_start=True)

    @classmethod
    def start(cls, force_start=False):

        if Queue.is_locked():
            if not force_start:
                return

        force = "--force" if force_start else ""

        subprocess.Popen(
            [
                sys.executable,
                str(pathlib.Path(APP_DIR, "scripts", "schedule.py")),
                force,
            ]
        )

    @classmethod
    def jobs(cls):
        return cls.select().where(cls.obj_type != QueueObjType.CONTROL)

    @classmethod
    def reset_failed(cls, blog):
        now = datetime.datetime.utcnow()
        Queue.update(
            status=QueueStatus.WAITING, date_inserted=now, date_updated=now,
        ).where(Queue.status == QueueStatus.FAILED, Queue.blog == blog,).execute()

    @classmethod
    def add_control(cls, blog):
        return Queue.create(
            obj_type=QueueObjType.CONTROL, blog=blog, status=QueueStatus.WAITING
        )

    @classmethod
    def _control_jobs(cls, blog=None):
        jobs = (
            cls.select()
            .where(cls.obj_type == QueueObjType.CONTROL)
            .order_by(cls.date_inserted.asc())
        )
        if blog is not None:
            jobs = jobs.where(cls.blog == blog)
        return jobs

    @classmethod
    def control_jobs(cls, blog=None):
        jobs = cls._control_jobs()
        if blog is not None:
            try:
                jobs = jobs.where(cls.blog == blog).get()
            except Queue.DoesNotExist:
                return None
        return jobs

    @classmethod
    def is_locked(cls, blog=None):
        ctl = cls.control_jobs(blog)
        if blog is None:
            try:
                ctl = ctl.get()
            except Queue.DoesNotExist:
                return False
        if ctl is None:
            return False
        return ctl.status == QueueStatus.RUNNING

    @classmethod
    def run_queue_(cls, blog=None):

        if blog is not None:
            cls.add_control(blog)
            print(f"Adding control job for blog {blog.id}.")

        while True:

            try:
                job = cls.control_jobs().get()
            except Queue.DoesNotExist:
                print("No more control jobs.")
                break

            blog = job.blog

            total = 0
            print(f"Starting run for blog {blog.id}")

            job.lock()

            begin = clock()

            while True:
                count, timer = cls.run(job, batch_time_limit=2.0)
                if not count:
                    break
                try:
                    job = Queue.get_by_id(job.id)
                except Queue.DoesNotExist:
                    print("Queue run interrupted.")
                    break
                if job.status != QueueStatus.RUNNING:
                    print("Queue run interrupted.")
                    break

                total += count
                print(
                    f"{count} jobs in {timer:.3f} secs. {blog.queue_jobs().count()} remaining."
                )
                job.date_updated = datetime.datetime.utcnow()
                job.save()
                sleep(random.random())

            print(
                f"Finished {total} jobs for blog {blog.id} in {clock()-begin:.3f} secs."
            )

            failures = cls.failures(blog).count()
            if failures:
                print(f"WARNING: {failures} job(s) failed to publish.")

            if job.status == QueueStatus.RUNNING:
                job.delete_instance()
            else:
                break

    @classmethod
    def run_immediately(cls, blog):
        # This must be called from within a db context!
        job = Queue.add_control(blog)
        cls.run.__wrapped__(cls, job)
        job.delete_instance()

    @classmethod
    @db_context
    def run(cls, job, batch_count=None, batch_time_limit=None):
        gc.disable()
        blog = job.blog
        batch = (
            cls.select()
            .where(
                cls.blog == blog,
                cls.obj_type != QueueObjType.CONTROL,
                cls.status != QueueStatus.FAILED,
                cls.date_inserted <= job.date_inserted,
            )
            .order_by(cls.priority.desc())
        )

        if batch_count:
            batch = batch.limit(batch_count)

        start_time = clock()
        last_time = 0.0
        count = 0

        item: Queue

        for item in batch:
            try:
                f = item.fileinfo
                t = item.obj_type
                if t == QueueObjType.WRITE_FILEINFO:
                    if f.preview_built:
                        f.clear_preview_file()
                    f.write_file()
                elif t == QueueObjType.DEL_FILEINFO:
                    if f.preview_built:
                        f.clear_preview_file()
                    f.remove_file()
                elif t == QueueObjType.DEL_FILE:
                    delpath = pathlib.Path(blog.base_filepath, item.text_data)
                    if delpath.exists():
                        os.remove(str(delpath))
            except TemplateError as e:
                item.status = QueueStatus.FAILED
                try:
                    item.failure_data = str(e)
                # ? don't know if we need this anymore, test it
                except Exception as ee:
                    item.failure_data = str(ee)
                item.save()
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                item.status = QueueStatus.FAILED
                item.failure_data = (
                    "".join(traceback.format_tb(exc_traceback)) + "\n" + str(e)
                )
                item.save()
            else:
                item.delete_instance()

            count += 1
            last_time = clock() - start_time
            if batch_time_limit:
                if last_time > batch_time_limit:
                    break

        gc.enable()
        return count, last_time


class ArchiveContext:

    settings = settings

    # TODO: consolidate all next/previous into a single property on the post itself.

    context_cache = {}

    def __init__(self, context_obj, template_mapping):
        self.mapping = template_mapping
        # self.template = template_mapping.template
        self.template = Template._dbcache(template_mapping.template_id)
        self._context_obj = context_obj
        self.types = TemplateType
        self.blog = None
        self.post = None
        self.posts = None
        self.year = None
        self.month = None
        self.date = None
        self.category = None
        self.tag = None

        if isinstance(context_obj, Post):
            self._from_post(context_obj)
        elif isinstance(context_obj, FileInfo):
            self._from_fileinfo(context_obj)

    def datefmt(self, date, str):
        return date.strftime(str)

    def _setdate(self):
        if not self.year:
            self.date = None
            return
        self.date = datetime.datetime(
            year=self.year, month=self.month if self.month else 1, day=1
        )

    def _from_post(self, post: Post):
        self.blog = post.blog
        self.post = post
        self.posts = self.blog.published_posts
        self.year = post.date_published.year
        self.month = post.date_published.month
        self.categories = self.blog.categories
        self.category = post.primary_category
        self.permalink = self.post.permalink
        self._setdate()

    @property
    def permalink_idx(self):
        return self.permalink.rsplit(
            f"/{self.blog.indexfile}.{self.blog.base_filetype}", 1
        )[0]

    def _from_fileinfo(self, fileinfo: FileInfo):
        self._fileinfo = fileinfo
        self.blog = fileinfo.blog
        self.permalink = f"{self.blog.permalink}/{fileinfo.filepath}"
        self.categories = self.blog.categories
        current_context = self.blog.published_posts
        self.top_context = current_context
        c: Context
        year = None
        month = None
        category = None
        tag = None
        for c in fileinfo.context:
            if c.context_type == "Y":
                year = c.context_id
                current_context = current_context.where(
                    Post.date_published >= datetime.datetime(year=year, month=1, day=1),
                    Post.date_published
                    < datetime.datetime(year=year + 1, month=1, day=1),
                )
            elif c.context_type == "m":
                if not year:
                    raise Exception("No year provided")
                month = c.context_id
                som = datetime.datetime(year=year, month=month, day=1)
                current_context = current_context.where(
                    Post.date_published >= som, Post.date_published < next_month(som),
                )
            elif c.context_type == "C":
                category: Category = Category.get_by_id(c.context_id)
                cat_posts = category.published_posts.select(Post.id)
                current_context = current_context.where(Post.id << cat_posts)
                self.top_context = current_context
            elif c.context_type == "t":
                tag: Tag = Tag.get_by_id(c.context_id)
                tag_posts = tag.published_posts
                current_context = current_context.where(Post.id << tag_posts)
                self.top_context = current_context

        self.posts = current_context
        self.year = year
        self.month = month
        self.category = category
        self.tag = tag
        self._setdate()

    @property
    def posts_desc(self):
        return self.posts.order_by(Post.date_published.desc(), Post.id.desc())

    @property
    def posts_alpha(self):
        return self.posts.order_by(Post.title)

    @property
    def next_post(self):
        if self.post is None:
            return None

        try:
            return (
                self.blog.published_posts.where(
                    (Post.date_published > self.post.date_published)
                    | (
                        (
                            (Post.date_published == self.post.date_published)
                            & (Post.id > self.post.id)
                        )
                    )
                )
                .order_by(Post.date_published.asc(), Post.id.asc())
                .limit(1)
                .get()
            )

        except Post.DoesNotExist:
            return None

    @property
    def previous_post(self):
        if self.post is None:
            return None

        try:

            return (
                self.blog.published_posts.where(
                    (Post.date_published < self.post.date_published)
                    | (
                        (
                            (Post.date_published == self.post.date_published)
                            & (Post.id < self.post.id)
                        )
                    )
                )
                .order_by(Post.date_published.desc(), Post.id.desc())
                .limit(1)
                .get()
            )

        except Post.DoesNotExist:
            return None

    @property
    def next(self):
        if self.post:
            return None

        try:
            next_start_date = self.posts[0].date_published
        except IndexError:
            return None

        last_context = self._fileinfo.context[-1]

        if last_context.context_type == "Y":
            start_date = datetime.datetime(
                year=next_start_date.year + 1, month=1, day=1
            )
        elif last_context.context_type == "m":
            start_date = next_month(next_start_date)
        else:
            return None

        tag = None
        category = None

        cc = Context.select(Context.fileinfo)

        for n in self._fileinfo.context:
            if n.context_type == "t":
                tag = cc.where(
                    Context.context_type == "t", Context.context_id == n.context_id
                )
            if n.context_type == "C":
                category = cc.where(
                    Context.context_type == "C", Context.context_id == n.context_id
                )

        try:
            result = (
                self.top_context.where(Post.date_published >= start_date)
                .order_by(Post.date_published.asc())
                .limit(1)
                .get()
            )

            if tag or category:
                result = result.fileinfos
            if tag:
                result = result.where(FileInfo.id << tag)
            if category:
                result = result.where(FileInfo.id << category)

        except (Post.DoesNotExist, FileInfo.DoesNotExist):
            return None

        return self._new_context(result)

    @property
    def previous(self):
        if self.post:
            return None

        try:
            previous_start_date = self.posts[0].date_published
        except IndexError:
            return None

        last_context = self._fileinfo.context[-1]
        if last_context.context_type == "Y":
            start_date = datetime.datetime(
                year=previous_start_date.year, month=1, day=1
            ) - datetime.timedelta(seconds=1)
        elif last_context.context_type == "m":
            start_date = previous_month(previous_start_date)
        else:
            return None

        tag = None
        category = None
        cc = Context.select(Context.fileinfo)

        for n in self._fileinfo.context:
            if n.context_type == "t":
                tag = cc.where(
                    Context.context_type == "t", Context.context_id == n.context_id
                )
            if n.context_type == "C":
                category = cc.where(
                    Context.context_type == "C", Context.context_id == n.context_id
                )

        try:
            result = (
                self.top_context.where(Post.date_published <= start_date)
                .order_by(Post.date_published.desc())
                .limit(1)
                .get()
            )

            if tag or category:
                result = result.fileinfos
            if tag:
                result = result.where(FileInfo.id << tag)
            if category:
                result = result.where(FileInfo.id << category)

        except (Post.DoesNotExist, FileInfo.DoesNotExist):
            return None

        return self._new_context(result)

    def _new_context(self, result):
        if isinstance(result, Post):
            result = result.fileinfos
        result = result.where(FileInfo.templatemapping == self.mapping).get()
        return ArchiveContext(result, self.mapping)

    def posts_in_categories(self, category_list):
        cat_list = Category.select().where(Category.title << category_list)
        posts_in_cat = PostCategory.select(PostCategory.post).where(
            PostCategory.category << cat_list
        )
        return self.posts_desc.where(Post.id << posts_in_cat)

    def posts_with_metadata(self, key, value=None):
        m1 = Metadata.select(Metadata.object_id).where(
            Metadata.object_name == "post",
            Metadata.key == key,
            Metadata.object_id << self.posts.select(Post.id),
        )
        if value:
            m1 = m1.where(Metadata.value == value)

        m2 = self.posts.where(Post.id << m1)
        return m2


class _System(MetadataModel):
    class _meta:
        table_name = "_system"

    id = 0
    title = "System"
    permalink = "/"
    queue_manage_link = "/queue"
    manage_link = "/"

    @classmethod
    def queue_badge(cls):
        style = "success"
        queue_count = Queue.select().count()
        if Queue.failures():
            style = "danger"
        return (
            f'<span id="queue-badge" class="badge badge-{style}">{queue_count}</span>'
        )


System = _System()

Blog.sorting = {
    "status": {"asc": Post.status, "desc": Post.status.desc(),},
    "pub": {"asc": Post.date_published, "desc": Post.date_published.desc(),},
    "title": {"asc": Post.title, "desc": Post.title.desc(),},
    "id": {"asc": Post.id, "desc": Post.id.desc(),}
    # TODO: author and category may prove tricky
}
Blog.filtering = {
    "status": {
        "draft": lambda model, listing: listing.where(
            Post.status == PublicationStatus.DRAFT
        )
    }
}
