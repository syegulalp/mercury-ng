from cms.models.enums import TemplatePublishingMode, TemplateType, UserPermission
from bottle import route, template, request, redirect
from ..models import (
    Blog,
    Template,
    User,
    Queue,
    unsafe,
    db_context,
    FileInfo,
    Post,
    FileInfoMapping,
    FileInfo,
    Theme,
    Context,
)
from .ui import format_grid, make_menu, make_buttons, Tab, Notice, Button
from .context import blog_context, user_context, template_context, bt_gen
from ..settings import PRODUCT_NAME, PRODUCT_VERSION

import hashlib
import json

template_tabs = {
    "index": Tab("Index", "/blog/{tabitem.id}/templates"),
    "post": Tab("Post", "/blog/{tabitem.id}/templates/post"),
    "archive": Tab("Archive", "/blog/{tabitem.id}/templates/archive"),
    "include": Tab("Include", "/blog/{tabitem.id}/templates/include"),
    "ssi": Tab("SSI", "/blog/{tabitem.id}/templates/ssi"),
    "media": Tab("Media", "/blog/{tabitem.id}/templates/media"),
}

template_tabs_filter = {
    "index": TemplateType.INDEX,
    "post": TemplateType.POST,
    "archive": TemplateType.ARCHIVE,
    "include": TemplateType.INCLUDE,
    "ssi": TemplateType.SSI,
    "media": TemplateType.MEDIA,
}

template_sidebar = {
    "Publishing": "template/publish",
}


@route("/blog/<blog_id:int>/new-template/<template_type>", method=("GET", "POST"))
def new_template(blog_id: int, template_type: str):
    redirect_ok, result = new_template_core(blog_id, template_type)
    if redirect_ok:
        return redirect(result)
    return result


@db_context
@blog_context
@user_context(UserPermission.DESIGNER)
def new_template_core(user: User, blog: Blog, template_type: str):

    notice = Notice()

    blog_template: Template = Template(
        theme=blog.theme,
        title="",
        text="",
        template_type=template_tabs_filter[template_type],
        publishing_mode=TemplatePublishingMode.QUEUE,
    )

    default_mapping = ""

    if request.method == "POST":
        blog_template.title = request.forms.template_title
        blog_template.text = request.forms.template_text
        default_mapping = request.forms.template_mapping

        if blog_template.title == "":
            notice.fail("Templates must have a title.")

        if (
            blog_template.template_type in (TemplateType.INDEX, TemplateType.SSI)
            and default_mapping == ""
        ):
            notice.fail("You must provide a default mapping.")

        if notice.is_ok():
            blog_template.save()
            blog_template.add_mapping(default_mapping)

            if blog_template.template_type in (TemplateType.INDEX, TemplateType.SSI):
                blog_template.build_fileinfos()

            # TODO: indicate that fileinfos have to be build for this template
            # maybe launch that in a separate tab?

            Template.clear_cache()

            return True, blog_template.manage_link

    return (
        False,
        template(
            "template-edit.tpl",
            tpl=blog_template,
            menu=make_menu("new_template", blog),
            notice=notice,
            default_mapping=default_mapping,
            blog=blog,
            page_title=f"Creating new template for {bt_gen(blog)}",
        ),
    )


@route("/blog/<blog_id:int>/templates")
@route("/blog/<blog_id:int>/templates/<tab>")
@db_context
@blog_context
@user_context(UserPermission.DESIGNER)
def blog_templates(user: User, blog: Blog, tab: str = "index"):

    templates = (
        Template.select()
        .where(
            Template.theme == blog.theme,
            Template.template_type == template_tabs_filter[tab],
        )
        .order_by(Template.title)
    )

    buttons = make_buttons(
        (Button(f"Create new {tab} template", Template.create_link(blog, tab)),)
    )

    grid = format_grid(templates, buttons=buttons)

    return template(
        "default.tpl",
        tabs=template_tabs,
        tab=tab,
        menu=make_menu("templates_category", [blog, template_tabs[tab].title]),
        text=grid,
        blog=blog,
        tabitem=blog,
        page_title=f"Templates for {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/template/<template_id:int>/edit")
@db_context
@template_context
@user_context(UserPermission.DESIGNER)
def edit_template(user: User, blog_template: Template, blog_id):

    notice = Notice()
    if (
        blog_template.template_type not in (TemplateType.INCLUDE, TemplateType.MEDIA)
        and blog_template.fileinfos.count() == 0
    ):
        notice.fail(
            f'This template has no fileinfos created for it yet. <a target="_blank" href="{blog_template.blog.manage_link}/create-fileinfos/{blog_template.id}">Click here to build fileinfos in the background.</a>'
        )

    script = f"""
<script>
    var template_id = {blog_template.id};
</script>
<script src="/static/js/notify.js?{PRODUCT_VERSION}"></script>
<script src="/static/js/template-edit.js?{PRODUCT_VERSION}"></script>"""

    return template(
        "template-edit.tpl",
        tpl=blog_template,
        notice=notice,
        blog=blog_template.blog,
        post_footer=script,
        menu=make_menu("template_menu", blog_template),
        default_mapping=blog_template.default_mapping.mapping
        if blog_template.template_type not in (TemplateType.INCLUDE, TemplateType.MEDIA)
        else None,
        page_title=f"Editing template {blog_template.title} ({blog_template.id}) / {bt_gen(blog_template.blog)}",
    )


@route("/blog/<blog_id:int>/template/<template_id:int>/save", method="POST")
@db_context
@template_context
@user_context(UserPermission.DESIGNER)
def save_template(user: User, blog_template: Template, blog_id):

    invalidate = False
    redir = ""

    notice = Notice()

    save_action = request.forms.save_action

    blog_template.title = request.forms.template_title
    blog_template.text = request.forms.template_text.replace("\r", "")
    if blog_template.template_type not in (
        TemplateType.INCLUDE,
        TemplateType.MEDIA,
        TemplateType.SSI,
    ):
        blog_template.publishing_mode = TemplatePublishingMode(
            int(request.forms.publishing_mode)
        )
    blog_template.save()

    notice.ok(
        f"Template <b>{unsafe(blog_template.title)}</b> (#{blog_template.id}) saved."
    )

    Template.clear_cache()

    if blog_template.template_type not in (TemplateType.INCLUDE, TemplateType.MEDIA):
        default_mapping = blog_template.default_mapping

        old_mapping = default_mapping.mapping
        new_mapping = request.forms.template_mapping

        if old_mapping != new_mapping:
            invalidate = True
            default_mapping.dequeue()
            default_mapping.clear_fileinfos()
            default_mapping.mapping = new_mapping
            default_mapping.save()
            notice.ok("Template mapping recreated.")

            if blog_template.template_type in (TemplateType.INDEX, TemplateType.SSI):
                blog_template.build_fileinfos()

    if blog_template.template_type in (TemplateType.INDEX, TemplateType.SSI):
        invalidate = False
        for fileinfo in blog_template.fileinfos.where(FileInfo.preview_built == True):
            fileinfo.clear_preview_file()

    if invalidate:
        notice.ok(
            "This blog should be republished to reflect changes to this template's mappings."
        )

    if request.forms.save_action == "save_only":
        pass
    elif request.forms.save_action == "save_and_republish":
        if blog_template.publishing_mode != TemplatePublishingMode.DO_NOT_PUBLISH:
            blog_template.dequeue_failed()
            if blog_template.template_type in (TemplateType.INDEX, TemplateType.SSI):
                for f in blog_template.fileinfos:
                    f.clear_preview_file()
                    f.write_file()
                notice.ok("Template files rebuilt.")
            else:
                # TODO: replace with enqueue of posts via refresh
                # blog_template.enqueue(manual_ok=True)
                # Queue.start(force_start=True)
                # notice.ok("Template files sent to queue.")
                redir = f"{blog_template.blog.manage_link}/republish-template/{blog_template.id}"

    sidebar = template(
        "include/sidebar/base.tpl",
        tpl=blog_template,
        is_new=False,
        sidebar_items=template_sidebar,
        template=template,
        TemplateType=TemplateType,
        TemplatePublishingMode=TemplatePublishingMode,
    )

    msg = template("include/notice.tpl", notice=notice)

    return json.dumps([sidebar, msg, redir])
    # `return f"<div>{sidebar}</div><div>{msg}</div><div>{redir}</div>"


@route("/blog/<blog_id:int>/template/<template_id:int>/republish")
@db_context
@template_context
@user_context(UserPermission.DESIGNER)
def republish_template(
    user: User, blog_template: Template, blog_id,
):
    blog_template.enqueue()
    Queue.start(blog_template.blog)


@route("/blog/<blog_id:int>/template/<template_id:int>/delete", method=("GET", "POST"))
@db_context
@template_context
@user_context(UserPermission.DESIGNER)
def delete_teplate(user: User, blog_template: Template, blog_id):

    notice = Notice()

    confirmation = hashlib.sha256(
        blog_template.title.encode("utf-8") + str(user.id).encode("utf-8")
    ).hexdigest()

    if request.method == "GET":
        notice.warning(
            "Are you sure you want to delete this template?",
            "delete",
            confirmation,
            blog_template.manage_link,
        )

    else:

        confirm_key = request.forms.action_key
        if not confirm_key:
            notice.fail("No delete key provided")

        if confirm_key == confirmation:
            blog_template.delete_instance(recursive=True)
            notice.ok("Template deleted.")

        else:
            notice.fail("No delete key provided")

    return template(
        "default.tpl",
        menu=make_menu("template_menu", blog_template),
        page_title=f"Deleting template {blog_template.title} ({blog_template.id}) {bt_gen(blog_template.blog)}",
        notice=notice,
        text="",
        blog=blog_template.blog,
    )


@route("/blog/<blog_id:int>/template/<template_id:int>/preview")
@route("/blog/<blog_id:int>/template/<template_id:int>/preview/<post_id:int>")
def preview_template(blog_id: int, template_id: int, post_id=None):
    try:
        result = preview_template_core(template_id, blog_id, post_id)
    except Exception as e:
        return f"<pre>{e}</pre>"
    else:
        return redirect(result)


@db_context
@template_context
@user_context(UserPermission.DESIGNER)
def preview_template_core(user: User, blog_template: Template, blog_id, post_id):

    blog = blog_template.blog

    if blog_template.template_type in (
        TemplateType.SSI,
        TemplateType.INCLUDE,
        TemplateType.INDEX,
    ):
        f = blog_template.default_mapping.fileinfos[0]
    else:
        if post_id is None:
            preview_post = (
                blog.published_posts.order_by(Post.date_published.desc()).limit(1).get()
            )
        else:
            try:
                preview_post = blog.posts.where(Post.id == post_id).get()
            except Post.DoesNotExist:
                raise Exception(f"Post #{post_id} does not exist")

        f: FileInfo

        # use primary category for post

        default_cat_ctx = Context.select(Context.fileinfo).where(
            Context.context_id == preview_post.primary_category,
            Context.context_type == "C",
        )

        default_fileinfo = blog_template.default_mapping.fileinfos.where(
            FileInfo.id << default_cat_ctx
        )

        if not default_fileinfo.count():
            default_fileinfo = blog_template.default_mapping.fileinfos

        f = (
            FileInfoMapping.select()
            .where(
                FileInfoMapping.post == preview_post,
                FileInfoMapping.fileinfo << default_fileinfo,
            )
            .get()
            .fileinfo
        )

    f.write_preview_file()
    return f"{blog.permalink}/{f.preview_filepath}"


@route("/blog/<blog_id:int>/themes")
@db_context
@blog_context
@user_context(UserPermission.DESIGNER)
def blog_themes(user: User, blog: Blog):
    themes = Theme.select().where(Theme.blog_id.is_null())
    text = format_grid(themes, listing_fmt={"blog_context": blog})

    return template(
        "default.tpl",
        text=text,
        menu=make_menu("blog_themes", blog),
        page_title=f"Themes for {blog.title} / ({PRODUCT_NAME})",
        blog=blog,
    )
