from cms.models.enums import PublicationStatus
import pathlib
from bottle import route, template, request
from cms.models import Blog, User, db_context, Media, UserPermission, Post
from cms.routes.ui import format_grid, make_menu, make_buttons, Button, Notice
from cms.routes.context import blog_context, user_context, generate_blog_title
from cms.routes.utils import upload_script
from cms.settings import PRODUCT_VERSION
import hashlib, os, datetime


@route("/blog/<blog_id:int>/media")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def media_menu(user: User, blog: Blog, search_term=None):

#     script = f"""<script>
# var upload_path = "{blog.upload_link}";
# function refreshMediaList(){{}};
# </script>
# <script src="/static/js/drop.js"></script>"""

    script = upload_script(
        upload_path = blog.upload_link,
        refresh_media=True
    )

    media = blog.media.order_by(Media.date_created.desc())

    if search_term is not None:
        media = blog.media_search(search_term, media)
        menu = make_menu("blog_media_search", (blog, search_term))
    else:
        menu = make_menu("blog_media", blog)

    buttons = make_buttons(
        (
            Button("Search", blog.media_search_link),
            Button("Upload (advanced)", blog.upload_advanced_link, "info"),
        )
    )

    text = format_grid(media, buttons=buttons)

    return template(
        "default.tpl",
        text=text,
        blog=blog,
        post_footer=script,
        search=search_term,
        menu=menu,
        request=request,
        page_title=f"Media for {generate_blog_title(blog)}",
    )


@route("/blog/<blog_id:int>/media-search")
def media_search(blog_id):
    search_term = request.query.query
    return media_menu(blog_id, search_term)


@route("/blog/<blog_id:int>/media-upload", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def media_upload_advanced(user: User, blog: Blog):

    custom_upload_path = ""
    file_prefix = ""
    notice = Notice()

    upload_link = blog.upload_link

    if request.method == "POST":
        if ".." not in request.forms.custom_upload_path:
            custom_upload_path = request.forms.custom_upload_path
        else:
            notice.fail("Invalid path.")

        file_prefix = request.forms.file_prefix or ""

        if request.forms.post_association:
            try:
                post: Post = Post.get(id=int(request.forms.post_association), blog=blog)
            except Exception:
                notice.fail(f"Post ID {request.forms.post_association} is not valid.")
            else:
                upload_link = post.upload_link

#     script = f"""<script>
# var upload_path = "{upload_link}";
# var uploadFilePath = "{custom_upload_path}";
# function refreshMediaList(){{}};
# </script><script src="/static/js/drop.js"></script>
# """

    script = upload_script(
        upload_path=upload_link,
        upload_file_path=custom_upload_path,
        refresh_media=True
    )

    text = template(
        "include/upload.tpl",
        custom_upload_path=custom_upload_path,
        blog=blog,
        upload_option=request.forms.upload_option or "default",
        post_association=request.forms.post_association or "",
        file_prefix=file_prefix,
    )

    return template(
        "default.tpl",
        text=text,
        blog=blog,
        notice=notice,
        post_footer=script,
        menu=make_menu("blog_media", blog),
        page_title=f"Upload media for {generate_blog_title(blog)}",
    )


@route("/blog/<blog_id:int>/media/<media_id:int>/in")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def media_menu_in(user: User, blog: Blog, media_id: int):

    media_item: Media = Media.get_by_id(media_id)
    text = format_grid(media_item.posts)

    return template(
        "default.tpl",
        text=text,
        blog=blog,
        menu=make_menu("blog_media_item_in", media_item),
        page_title=f"Posts with media #{media_item.id} / {generate_blog_title(blog)}",
    )


@route("/blog/<blog_id:int>/media/<media_id:int>/edit", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def media_edit(user: User, blog: Blog, media_id: int):

    media_item: Media = Media.get_by_id(media_id)

    notice = Notice()

    script = f"""
    <script>
    var addMetadataLink = "{media_item.add_metadata_link}";
    var removeMetadataLink = "{media_item.remove_metadata_link}";
    </script>
    <script src="/static/js/typeahead.js?{PRODUCT_VERSION}"></script>
    <script src="/static/js/tinymce/tinymce.min.js?{PRODUCT_VERSION}"></script>
    <script src="/static/js/notify.js?{PRODUCT_VERSION}"></script>
    <script src="/static/js/metadata.js?{PRODUCT_VERSION}"></script>
    <script>metadataListInit();</script>
    """

    if request.method == "POST":

        old_description = media_item.friendly_name
        new_description = request.forms.friendly_name

        if old_description != new_description:
            media_item.friendly_name = new_description
            media_item.save()
            notice.ok("Detailed description updated.")

        parent_dir = media_item.full_filepath.parent
        old_filename = media_item.filename
        new_filename = request.forms.media_filename + "." + media_item.filename_parts[1]
        new_filepath = pathlib.Path(parent_dir, new_filename)
        media_item.filename = new_filename

        if old_filename != new_filename:

            for post in media_item.posts:
                if post.open_for_editing_by:
                    notice.fail(
                        f"Post #{post.id} uses this image and is open for editing. Release edit lock before continuing."
                    )

            if new_filepath.exists():
                notice.fail(
                    f"A file with the name {new_filename} already exists. Choose another name."
                )

            if notice.is_ok():

                old_url = f' src="{media_item.url}"'
                old_filepath = pathlib.Path(media_item.filepath).parent

                os.rename(str(media_item.full_filepath), str(new_filepath))
                notice.ok(f"File {old_filename} renamed to {new_filename}.")

                media_item.filepath = str(pathlib.Path(old_filepath, new_filename))
                media_item.date_last_modified = datetime.datetime.utcnow()
                media_item.save()

                new_url = f' src="{media_item.url}"'

                if not request.forms.no_rename:
                    post: Post
                    for post in media_item.posts:
                        post.text = post.text.replace(old_url, new_url)
                        post.save()
                        if post.status == PublicationStatus.PUBLISHED:
                            post.enqueue()

    text = template("include/media-edit.tpl", media=media_item)

    return template(
        "default.tpl",
        text=text,
        blog=blog,
        notice=notice,
        post_footer=script,
        menu=make_menu("blog_media_item", media_item),
        page_title=f"Edit media #{media_item.id} / {generate_blog_title(blog)}",
    )


@route("/blog/<blog_id:int>/media/<media_id:int>/delete", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def media_delete(user: User, blog: Blog, media_id: int):
    notice = Notice()
    media_item: Media
    media_item = Media.get(id=media_id, blog=blog)

    confirmation = hashlib.sha256(
        media_item.filename.encode("utf-8") + str(user.id).encode("utf-8")
    ).hexdigest()

    if request.method == "GET":
        notice.warning(
            f"Are you sure you want to delete media object {media_item.filename} (#{media_item.id})?",
            "delete",
            confirmation,
            media_item.manage_link,
        )

    else:

        confirm_key = request.forms.action_key
        if not confirm_key:
            notice.fail("No delete key provided")

        if confirm_key == confirmation:
            media_item.delete_file()
            media_item.delete_instance(recursive=True)
            notice.ok("Media object deleted.")

        else:
            notice.fail("No delete key provided")

    return template(
        "default.tpl",
        menu=make_menu("blog_media_item", media_item),
        page_title=f"Deleting media #{media_item.id} / {generate_blog_title(blog)}",
        notice=notice,
        text="",
        blog=blog,
    )


@route("/blog/<blog_id:int>/media/<media_id:int>/add-metadata", method="POST")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def add_metadata(user: User, blog: Blog, media_id: int):

    media_item = Media.get(id=media_id, blog=blog)
    new_key = request.forms.key
    new_value = request.forms.value
    media_item.set_metadata(new_key, new_value)

    return template("include/sidebar/post/metadata-sublist.tpl", post=media_item)


@route("/blog/<blog_id:int>/media/<media_id:int>/remove-metadata", method="POST")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def remove_metadata(user: User, blog: Blog, media_id: int):
    media_item = Media.get(id=media_id, blog=blog)
    new_key = request.forms.key
    media_item.del_metadata(new_key)

    return template("include/sidebar/post/metadata-sublist.tpl", post=media_item)
