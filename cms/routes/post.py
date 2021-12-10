from cms.models.models import MediaAssociation
from cms.models.enums import (
    PublicationStatus,
    Actions,
)

from bottle import route, template, request, redirect
from cms.models import (
    Blog,
    Post,
    User,
    Queue,
    db_context,
    Media,
    Template,
    Tag,
    Category,
    UserPermission,
    System,
)
from cms.routes.ui import make_menu, Notice, format_grid
from cms.routes.context import blog_context, user_context, post_context, bt_gen
from cms.models.utils import str_to_date, unsafe
from cms.settings import PRODUCT_VERSION

# TODO: all notices must have `unsafe`!
# have an unsafe string renderer for objects
# idea: accept an iterable, with unsafe() items

import datetime
import json
import pathlib
import hashlib

BLOG_SIDEBAR = {
    "Publishing": "post/publishing",
    "Post Status": "post/status",
    "Tags": "post/tags",
    "Categories": "post/categories",
    "Media": "post/media",
    "Metadata": "post/metadata",
}

POST_EDIT_FOOTER = """
<script>
    var mediaInsertLink = "{post.media_insert_link}";
    var mediaTemplatesLink = "{post.media_templates_link}";
    var blogPermalink = "{post.blog.permalink}";    
    var mediaRenderLink = "{post.media_render_link}";
    var tagFetchLink = "{post.blog.tag_fetch_link}";
    var addTagLink = "{post.add_tag_link}";
    var removeTagLink = "{post.remove_tag_link}";
    var addMetadataLink = "{post.add_metadata_link}";
    var removeMetadataLink = "{post.remove_metadata_link}";
    var blog_id = "{post.blog.id}";
</script>
<script src="/static/js/typeahead.js?{PRODUCT_VERSION}"></script>
<script src="/static/js/tinymce/tinymce.min.js?{PRODUCT_VERSION}"></script>
<script src="/static/js/notify.js?{PRODUCT_VERSION}"></script>
<script src="/static/js/metadata.js?{PRODUCT_VERSION}"></script>
<script src="/static/js/queue.js?{PRODUCT_VERSION}"></script>
<script src="/static/js/editor.js?{PRODUCT_VERSION}"></script>
"""


def editor_css():
    return System.get_metadata("theme").value or ""


@route("/blog/<blog_id:int>/new-post", method=("GET",))
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def new_post(user: User, blog: Blog):

    post = Post()
    post.blog = blog
    post.title = ""
    post.text = ""
    post.author = user
    post.basename = ""
    post.excerpt_ = ""

    script = f'<script>var alt_editor_css = "{editor_css()},";</script>'

    return template(
        "post-edit.tpl",
        menu=make_menu("new_post", post),
        page_title=f"New post in {bt_gen(blog)}",
        post=post,
        blog=blog,
        post_footer=script
        + POST_EDIT_FOOTER.format(post=post, PRODUCT_VERSION=PRODUCT_VERSION),
    )


@route("/blog/<blog_id:int>/new-post", method=("POST",))
def new_post_save(blog_id):
    post = new_post_save_core(blog_id)
    return redirect(post.manage_link)


@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def new_post_save_core(user: User, blog: Blog):
    post: Post = Post.create(
        blog=blog,
        title=request.forms.post_title,
        text=request.forms.post_text,
        excerpt_=request.forms.post_excerpt,
        author=user,
        open_for_editing_by=user,
        basename="",
    )
    post.basename = post.create_basename()
    post.save()

    primary_category = int(request.forms.primary_category)
    new_category_obj = Category.get_by_id(primary_category)
    post.set_primary_category(new_category_obj)

    subcategories = set(int(_) for _ in request.forms.getlist("subcategory"))
    for subcategory in subcategories:
        new_category_obj = Category.get_by_id(subcategory)
        post.add_subcategory(new_category_obj)

    post.build_fileinfos()
    return post


@route("/blog/<blog_id:int>/post/<post_id:int>")
def edit_redirect(blog_id, post_id):
    return redirect(f"/blog/{blog_id}/post/{post_id}/edit")


@route("/blog/<blog_id:int>/post/<post_id:int>/live")
def live_redirect(blog_id, post_id):
    try:
        post = (
            Post.select()
            .where(
                Post.id == post_id,
                Post.blog == blog_id,
                Post.status == PublicationStatus.PUBLISHED,
            )
            .get()
        )
    except Post.DoesNotExist:
        return "No such post or post not live"
    return redirect(post.permalink)


def edit_page_title(post: Post):
    return f"Edit: {post.title} (#{post.id}) / {bt_gen(post.blog)}"


@route("/blog/<blog_id:int>/post/<post_id:int>/edit")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def edit_post(user: User, post: Post):

    if not post.open_for_editing_by:
        post.open_for_editing_by = user
        post.save()
    else:
        if post.open_for_editing_by != user:
            raise Exception("Post already open for editing")

    if post.excerpt_ is None:
        post.excerpt_ = ""

    script = f"""<script>
var upload_path = "{post.upload_link}";
var alt_editor_css = "{editor_css()},";
</script>
<script src="/static/js/drop.js"></script>"""

    return template(
        "post-edit.tpl",
        menu=make_menu("edit_post", post),
        post=post,
        blog=post.blog,
        post_footer=script
        + POST_EDIT_FOOTER.format(post=post, PRODUCT_VERSION=PRODUCT_VERSION),
        page_title=edit_page_title(post),
    )


def save_post_(post: Post, blog: Blog, notice: Notice, save_action: str):
    title_changed = False
    text_changed = False
    date_changed = False
    basename_changed = False
    categories_changed = False
    otherwise_dirty = False
    remake_fileinfo = False

    original_title = post.title
    original_text = post.text
    original_date = post.date_published
    original_basename = post.basename

    post.title = request.forms.post_title
    post.text = request.forms.post_text
    post.excerpt_ = (
        None if request.forms.post_excerpt == "" else request.forms.post_excerpt
    )
    post.date_published = str_to_date(request.forms.date_published)
    post.date_last_modified = datetime.datetime.utcnow()

    _basename = request.forms.get("post_basename", None)
    if _basename is not None:
        post.basename = _basename

    new_primary_category = int(request.forms.primary_category)
    if post.primary_category.id != new_primary_category:
        categories_changed = True
        new_primary_category_obj = Category.get_by_id(new_primary_category)
        post.set_primary_category(new_primary_category_obj)
        notice.ok(f"New primary category set: {new_primary_category_obj.title}")

    form_subcategories = set(int(_) for _ in request.forms.getlist("subcategory"))
    post_subcategories = set(_.id for _ in post.subcategories)
    new_categories = form_subcategories.difference(post_subcategories)

    for subcategory in post.subcategories:
        if subcategory.id not in form_subcategories:
            categories_changed = True
            post.remove_subcategory(subcategory)
            notice.ok(f"Subcategory removed: {subcategory.title}")

    if len(new_categories):
        categories_changed = True
        for new_subcategory in new_categories:
            new_subcategory_obj = Category.get_by_id(new_subcategory)
            if new_subcategory_obj != post.primary_category:
                post.add_subcategory(new_subcategory_obj)
                notice.ok(f"Subcategory added: {new_subcategory_obj.title}")

    if original_title != post.title:
        title_changed = True
    if original_text != post.text:
        text_changed = True

    # Change of title or text is not enough to trigger a remake of fileinfo
    # but is worth recording for future use

    if original_date != post.date_published:
        date_changed = True
    if original_basename != post.basename:
        basename_changed = True
        post.basename = post.create_basename()
    if post.is_dirty is not None:
        post.is_dirty = None
        otherwise_dirty = True

    if basename_changed or date_changed or categories_changed or otherwise_dirty:
        remake_fileinfo = True

    if remake_fileinfo:
        # This is to queue the post's OLD neighbors
        if post.status == PublicationStatus.PUBLISHED:
            post.enqueue(indices=False)
            post.dequeue_post_archives()
            post.queue_erase_post_archive_files()

        post.clear_fileinfos()
        post.build_fileinfos()

    if save_action not in (Actions.Preview.PREVIEW_ONLY,):
        post.save()
        notice.ok(f"Post {post.title_for_display} saved successfully.")

    if post.status == PublicationStatus.DRAFT:
        if save_action == Actions.Draft.SAVE_DRAFT:
            notice.ok(f"Draft updated.")

        elif save_action == Actions.Draft.SAVE_AND_SCHEDULE:

            if post.date_published < datetime.datetime.utcnow():
                notice.fail(
                    'Post was scheduled to go live in the past. Status not changed. To publish this post immediately, select "Save and publish now".'
                )
            else:
                post.status = PublicationStatus.SCHEDULED
                post.save()
                notice.ok(
                    f"Post is now scheduled to go live at <b>{post.date_published}</b>."
                )

        elif save_action == Actions.Draft.SAVE_AND_PUBLISH_NOW:

            post.status = PublicationStatus.PUBLISHED
            post.save()
            notice.ok("Post is now live.")
            post.enqueue()

    elif post.status == PublicationStatus.SCHEDULED:

        if save_action == Actions.Scheduled.SAVE_AND_UNSCHEDULE:
            post.status = PublicationStatus.DRAFT
            post.save()
            notice.ok("Post is no longer scheduled.")

        elif save_action == Actions.Scheduled.SAVE_AND_PUBLISH_NOW:
            post.status = PublicationStatus.PUBLISHED
            post.save()
            notice.ok("Post is now live.")
            post.enqueue()

    elif post.status == PublicationStatus.PUBLISHED:

        if save_action == Actions.Published.SAVE_AND_UPDATE_LIVE:
            post.permalink_fileinfo.write_file()
            notice.ok("Post updated live.")
            post.enqueue()

        elif save_action == Actions.Published.SAVE_DRAFT_ONLY:
            notice.ok("Draft updated; live post not changed.")

        elif save_action == Actions.Published.UNPUBLISH:
            post.unpublish()
            notice.ok("Post is no longer live.")

    return remake_fileinfo


@route("/blog/<blog_id:int>/post/<post_id:int>/save", method=("POST",))
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def save_post(user: User, post: Post):

    save_action = request.forms.save_action
    notice = Notice()

    blog: Blog = post.blog
    queue_count = blog.queue_items.count()
    remake_fileinfo = False

    try:
        remake_fileinfo = save_post_(post, blog, notice, save_action)
    except Exception as e:
        notice.fail(f"Error: {e}")

    post.update_index()

    final_queue_count = blog.queue_items.count() - queue_count

    if final_queue_count:
        notice.ok(f"<b>{final_queue_count} file(s)</b> sent to queue.")
        if not blog.get_metadata("no_autorun_queue"):
            Queue.start(blog)
    else:
        if post.status != PublicationStatus.DRAFT:
            notice.ok(
                "No files sent to queue. (Files may already be in process or nothing to enqueue.)"
            )

    if remake_fileinfo:
        notice.ok("Fileinfos rebuilt for post.")

    redir = ""
    popup = ""

    if save_action == Actions.CLOSE:
        post.open_for_editing_by = None
        post.save()
        redir = blog.manage_link

    elif save_action in (
        Actions.Preview.PREVIEW_ONLY,
        Actions.Preview.SAVE_AND_PREVIEW,
    ):
        notice.ok(f"Launched preview of post #{post.id}.")
        popup = post.preview_link

    sidebar = template(
        "include/sidebar/base.tpl",
        post=post,
        blog=blog,
        is_new=False,
        sidebar_items=BLOG_SIDEBAR,
        template=template,
    )

    msg = template("include/notice.tpl", notice=notice)
    queue_badge = blog.queue_badge()

    return json.dumps([sidebar, msg, popup, redir, queue_badge, edit_page_title(post)])

    # TODO: we should also lock template editing when pages are in queue (easy solution)
    # and perhaps keep the queue from running as long as any needed template is open for editing (need to track open/shut)
    # or use some kind of internal template versioning


@route("/blog/<blog_id:int>/queue-badge")
@db_context
@blog_context
def queue_button(blog: Blog):
    return blog.queue_badge()


@route("/blog/<blog_id:int>/post/<post_id:int>/preview")
def preview_post(blog_id: int, post_id: int):
    user, post = preview_core(blog_id, post_id)
    return redirect(
        f"{post.blog.permalink}/{post.preview_filepath}?{post.date_last_modified.timestamp()}"
    )


@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def preview_core(user: User, post: Post):
    post.permalink_fileinfo.write_preview_file()
    return user, post


@route("/blog/<blog_id:int>/post/<post_id:int>/media-insert")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def media_insert(user: User, post: Post):
    body = template("include/modal/media.tpl", post=post)
    return template("include/modal.tpl", modal_title="Select image", modal_body=body)


@route("/blog/<blog_id:int>/post/<post_id:int>/media-insert/refresh")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def media_insert_refresh(user: User, post: Post):
    return template("include/modal/media.tpl", post=post)


# TODO: move these to media at blog level


@route("/blog/<blog_id:int>/post/<post_id:int>/media-templates/<media_id:int>")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def media_tmplates(user: User, post: Post, media_id: int):
    media = Media.get(id=media_id, blog=post.blog)
    body = template("include/modal/media_templates.tpl", blog=post.blog, media=media)
    return template(
        "include/modal.tpl", modal_title="Select template for image", modal_body=body
    )


@route(
    "/blog/<blog_id:int>/post/<post_id:int>/media-render/<media_id:int>/<template_id:int>"
)
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def media_templates(user: User, post: Post, media_id: int, template_id: int):
    media = Media.get(id=media_id, blog=post.blog)
    tpl = Template.get(id=template_id)
    return tpl._cached().render(media=media)


@route("/blog/<blog_id:int>/post/<post_id:int>/media")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def media_json(user: User, post: Post):

    blog = post.blog
    text = format_grid(post.media.order_by(Media.id.desc()))
    script = f"""<script>var upload_path = "{post.upload_link}";
function refreshMediaList(){{}};
</script>
<script src="/static/js/drop.js"></script>"""
    return template(
        "default.tpl",
        post=post,
        blog=blog,
        text=text,
        post_footer=script,
        menu=make_menu("post_media_menu", post),
        page_title=f"Media for post #{post.id} / {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/post/<post_id:int>/upload", method="POST")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def file_upload(user: User, post: Post):
    return file_upload_core(user, post.blog, post)


def file_upload_core(user, blog: Blog, post=None):
    file_list = []

    for f in request.files.values():

        user_supplied_filepath = request.forms.filepath
        file_prefix = request.forms.file_prefix or None

        if user_supplied_filepath:
            initial_save_path = pathlib.Path(
                blog.base_media_directory, user_supplied_filepath
            )
            web_path = user_supplied_filepath

        else:
            initial_save_path = pathlib.Path(blog.media_upload_directory)
            web_path = blog.computed_media_upload_path

        if not initial_save_path.exists():
            initial_save_path.mkdir(parents=True)

        uploaded_filename, file_extension = f.filename.rsplit(".", 1)

        delimeter = 0

        if file_prefix:
            initial_filename = file_prefix
            final_filename = f"{initial_filename}-{delimeter}.{file_extension}"
        else:
            initial_filename = uploaded_filename
            final_filename = f"{initial_filename}.{file_extension}"

        while True:
            if pathlib.Path(initial_save_path, final_filename).exists():
                final_filename = f"{initial_filename}-{delimeter}.{file_extension}"
                delimeter += 1
            else:
                break

        final_save_path = pathlib.Path(initial_save_path, final_filename)

        f.save(str(final_save_path))

        new_media_item = Media.create(
            filename=final_filename,
            filepath=f"{web_path}/{final_filename}",
            friendly_name=final_filename,
            user=user,
            blog=blog,
        )

        if post is not None:
            new_assoc = MediaAssociation.create(media=new_media_item, post=post)

        file_list.append(
            {
                "filename": final_filename,
                "id": new_media_item.id,
                "url": new_media_item.url,
                "link": new_media_item.manage_link,
            }
        )
    return json.dumps(file_list)


@route("/blog/<blog_id:int>/post/<post_id:int>/add-tag", method="POST")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def add_tag(user: User, post: Post):
    blog: Blog = post.blog
    tag_to_add = request.forms.tag

    if len(tag_to_add) > 0:

        try:
            new_tag = blog.tags.where(Tag.title == tag_to_add).get()
        except Tag.DoesNotExist:
            new_tag = blog.add_tag(tag_to_add)

        try:
            post.tags.where(Tag.id == new_tag.id).get()
        except Tag.DoesNotExist:
            post.add_tag(new_tag)
            post.is_dirty = True
            post.save()

    return template("include/sidebar/post/tag-sublist.tpl", no_input=True, post=post)


@route("/blog/<blog_id:int>/post/<post_id:int>/remove-tag", method="POST")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def remove_tag(user: User, post: Post):
    blog: Blog = post.blog
    tag_to_remove = request.forms.tag

    try:
        new_tag = blog.tags.where(Tag.id == tag_to_remove).get()
    except Tag.DoesNotExist:
        pass
    else:
        post.remove_tag(new_tag)
        post.is_dirty = True
        post.save()

    return template("include/sidebar/post/tag-sublist.tpl", no_input=True, post=post)


@route("/blog/<blog_id:int>/post/<post_id:int>/add-metadata", method="POST")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def add_metadata(user: User, post: Post):
    new_key = request.forms.key
    new_value = request.forms.value
    post.set_metadata(new_key, new_value)

    return template("include/sidebar/post/metadata-sublist.tpl", post=post)


@route("/blog/<blog_id:int>/post/<post_id:int>/remove-metadata", method="POST")
@db_context
@post_context
@user_context(UserPermission.AUTHOR)
def remove_metadata(user: User, post: Post):
    new_key = request.forms.key
    post.del_metadata(new_key)

    return template("include/sidebar/post/metadata-sublist.tpl", post=post)


@route("/blog/<blog_id:int>/post/<post_id:int>/delete", method=("GET", "POST"))
@db_context
@post_context
@user_context(UserPermission.EDITOR)
def delete_post(user: User, post: Post, confirm_key=None):

    notice = Notice()

    confirmation = hashlib.sha256(
        post.title.encode("utf-8") + str(user.id).encode("utf-8")
    ).hexdigest()

    if request.method == "GET":
        notice.warning(
            f"Are you sure you want to delete blog post <b>{unsafe(post.title)}</b> ({post.id})?",
            "delete",
            confirmation,
            post.manage_link,
        )

    else:

        confirm_key = request.forms.action_key
        if not confirm_key:
            notice.fail("No delete key provided")

        if confirm_key == confirmation:
            post.delete_instance(recursive=True)
            notice.ok(f"Blog post <b>{unsafe(post.title)}</b> ({post.id}) deleted.")

        else:
            notice.fail("No delete key provided")

    return template(
        "default.tpl",
        menu=make_menu("all_blog_posts", post.blog),
        page_title=f"Deleting page {post.title} (#{post.id}) / {bt_gen(post.blog)}",
        notice=notice,
        text="",
        blog=post.blog,
    )


@route("/blog/<blog_id:int>/post/<post_id:int>/copy")
def copy_post(blog_id, post_id):
    new_post = copy_post_core(blog_id, post_id)
    return redirect(new_post.manage_link)


@db_context
@post_context
@user_context(UserPermission.EDITOR)
def copy_post_core(user: User, post: Post):
    old_post: Post
    old_post = Post.get(id=post.id)

    new_post = post
    new_post.id = None
    new_post.title += " (Copy)"
    new_post.status = PublicationStatus.DRAFT
    new_post.basename = new_post.create_basename()
    new_post.save()

    for category in old_post.categories:
        new_post.add_subcategory(category)
    for tag in old_post.tags:
        new_post.add_tag(tag)
    for media in old_post.media:
        MediaAssociation.create(post=new_post, media=media)
    for kv in old_post.get_metadata():
        new_post.set_metadata(kv.key, kv.value)

    new_post.clear_fileinfos()
    new_post.build_fileinfos()

    return new_post


@route("/blog/<blog_id:int>/post/<post_id:int>/add-media-ref", method="POST")
@db_context
@post_context
@user_context(UserPermission.EDITOR)
def add_media_ref(user: User, post: Post):
    media_item: Media = Media.get(id=int(request.forms.media_id), blog=post.blog)
    MediaAssociation.create(post=post, media=media_item)
    return ""


@route("/blog/<blog_id:int>/post/<post_id:int>/remove-media-ref", method="POST")
@db_context
@post_context
@user_context(UserPermission.EDITOR)
def add_media_ref_post(user: User, post: Post):
    media_item: Media = Media.get(id=int(request.forms.media_id), blog=post.blog)
    media_to_remove = MediaAssociation.get(post=post, media=media_item)
    media_to_remove.delete_instance()

    return ""


@route("/blog/<blog_id:int>/post/<post_id:int>/regen-basename", method="POST")
@db_context
@post_context
@user_context(UserPermission.EDITOR)
def regen_post_basename(user: User, post: Post):
    post.title = request.forms.title
    post.basename = None
    post.basename = post.create_basename()
    return post.basename
