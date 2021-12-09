# from cms.models.models import PostIndex
from bottle import route, template, request, redirect
from playhouse.shortcuts import model_to_dict

from cms.models import (
    Blog,
    Post,
    User,
    Category,
    db_context,
    Tag,
    UserPermission,
    Template,
    db,
)
from cms.models.models import PostCategory
from cms.models.utils import create_basename, fullpath
from cms.routes.ui import format_grid, make_menu, make_buttons, Button, Notice, Tab
from cms.routes.context import blog_context, user_context, bt_gen
from cms.routes.system import metadata_edit_, metadata_listing

from cms.routes.post import file_upload_core

import pathlib
from urllib.parse import urlparse, urlencode
from cms.settings import PRODUCT_NAME
import json
import zipfile
import hashlib

SETTINGS_TABS = {
    "": Tab("Name/Description", "/blog/{tabitem.id}/settings"),
    "media": Tab("Media", "/blog/{tabitem.id}/settings/media"),
    "url": Tab("URL/Filepath", "/blog/{tabitem.id}/settings/url"),
}


def close_search(link):
    qdict = dict(request.query)
    if "query" in qdict:
        qdict.pop("query")
    return Button("Close search", f"{link}?{urlencode(qdict)}", "info")


@route("/blog/<blog_id:int>")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def blogs_menu(user: User, blog: Blog, search_term=None):

    posts = blog.posts.order_by(Post.date_published.desc())

    if search_term is not None:
        posts = blog.search(search_term, posts)
        menu = make_menu("all_blog_posts_search", (blog, search_term))
        search_button = close_search(blog.manage_link)
    else:
        menu = make_menu("all_blog_posts", blog)
        search_button = Button(
            "Search", f"{blog.posts_search_link}?{request.query_string}", "info"
        )

    buttons = make_buttons(
        (Button("Create new post", blog.create_post_link), search_button)
    )

    text = format_grid(
        posts, buttons=buttons, search_query=search_term, sort_model=Blog
    )

    return template(
        "default.tpl",
        blog=blog,
        text=text,
        search=search_term,
        menu=menu,
        page_title=bt_gen(blog),
        request=request,
    )


@route("/blog/<blog_id:int>/search")
def blog_search(blog_id):
    search_term = request.query.query
    return blogs_menu(blog_id, search_term)


@route("/blog/<blog_id:int>/settings", method=("GET", "POST"))
@route("/blog/<blog_id:int>/settings/<tab>", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.DESIGNER)
def blog_settings(user: User, blog: Blog, tab: str = ""):

    if tab not in SETTINGS_TABS:
        tab = ""

    notice = Notice()
    current_blog: Blog = Blog.get_by_id(blog.id)

    if request.method == "POST":
        if tab == "":

            current_blog.title = request.forms.blog_title
            if current_blog.title == "":
                notice.fail("Your blog name must not be blank.")

            current_blog.description = request.forms.blog_description

        elif tab == "url":

            current_blog.base_filepath = request.forms.base_filepath
            if current_blog.base_filepath == "":
                notice.fail("Your blog's filepath must not be blank.")

            new_basepath = pathlib.Path(current_blog.base_filepath).resolve()
            if not new_basepath.exists():
                notice.ok(
                    "The filepath provided doesn't point to an existing directory, but one will be created at that location if possible. Note that any files from your <i>existing</i> blog's output directory will <i>not</i> be copied to the new directory; you must do that manually."
                )

            current_blog.base_url = request.forms.base_url
            if current_blog.base_url == "":
                notice.fail("Your blog's base URL must not be blank.")

            try:
                urlparse(current_blog.base_url)
            except Exception:
                notice.fail("The URL provided is not a valid URL.")

        elif tab == "media":
            current_blog.media_path = request.forms.media_path
            if current_blog.media_path == "":
                notice.fail("Your blog's media filepath must not be blank.")
            current_blog.media_upload_path = request.forms.media_upload_path
            new_media_path = pathlib.Path(
                current_blog.media_path, current_blog.computed_media_upload_path
            )
            try:
                fullpath(new_media_path)
            except:
                notice.fail(
                    "Your blog's media filepath and upload path do not resolve to a valid file path."
                )

        if notice.is_ok():
            current_blog.save()
            blog = current_blog
            Template.clear_cache()
            notice.ok("Changes saved. You should republish this blog.")

    settings = template("include/blog-settings.tpl", blog=blog, tab=tab)

    return template(
        "default.tpl",
        notice=notice,
        menu=make_menu("blog_settings_category", [blog, SETTINGS_TABS[tab].title]),
        tabs=SETTINGS_TABS,
        tab=tab,
        tabitem=blog,
        blog=current_blog,
        text=settings,
        page_title=f"Settings for {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/categories")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def blog_categories(user: User, blog: Blog):
    categories = blog.categories.order_by(Category.title.asc())
    buttons = make_buttons((Button("Create new category", blog.create_category_link),))
    text = format_grid(categories, buttons=buttons)
    return template(
        "default.tpl",
        text=text,
        menu=make_menu("blog_categories", blog),
        blog=blog,
        page_title=f"Categories in {bt_gen(blog)})",
    )


@route("/blog/<blog_id:int>/new-category", method=("GET", "POST"))
def new_blog_category(blog_id: int):
    result = new_blog_category_core(blog_id)
    if isinstance(result, Category):
        return redirect(result.edit_link)
    return result


# I still haven't figured out why we need to return the DB instance object
# in order for it to survive the @db_context mgr
# fortunately the workaround is not difficult


@db_context
@blog_context
@user_context(UserPermission.DESIGNER)
def new_blog_category_core(user: User, blog: Blog):

    notice = Notice()
    category = Category(blog=blog)

    if request.method == "POST":

        category_title = request.forms["category_title"]
        category_description = request.forms["category_description"]
        category_basename = request.forms["category_basename"]

        if not category_title:
            notice.fail("You must supply a category title")

        if not category_basename:
            notice.fail("You must supply a category basename")
        else:
            parts = []
            for part in category_basename.split("/"):
                parts.append(create_basename(part))
            category_basename = "/".join(parts)

        category = Category(
            title=category_title,
            description=category_description,
            basename=category_basename,
            blog=blog,
            default=False,
        )

        if notice.is_ok():
            category.save()
            return category

    text = template("include/category.tpl", category=category)

    return template(
        "default.tpl",
        text=text,
        menu=make_menu("new_blog_category", blog),
        blog=blog,
        page_title=f"New category / {bt_gen(blog)})",
        notice=notice,
    )


# TODO: actual editing for categories
# some way to stage/confirm changes?
# same as below, do it in passes in /edit/apply or sth


@route("/blog/<blog_id:int>/category/<category_id:int>/edit", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.DESIGNER)
def blog_category_edit(user: User, blog: Blog, category_id: int):
    category = Category.get_by_id(category_id)

    text = template("include/category.tpl", category=category)

    return template(
        "default.tpl",
        text=text,
        menu=make_menu("blog_category_edit", category),
        blog=blog,
        page_title=f"Category {category.title} / {bt_gen(blog)})",
    )


@route("/blog/<blog_id:int>/category/<category_id:int>/delete", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.DESIGNER)
def blog_category_delete(user: User, blog: Blog, category_id: int):

    category: Category
    category = Category.get_by_id(category_id)
    notice = Notice()
    action_key = hashlib.sha256(
        category.title.encode("utf-8") + str(user.id).encode("utf-8")
    ).hexdigest()

    c_id = request.query.get("c", 0)

    primary_cat_pages_ = Post.select().where(Post.primary_category == category)
    secondary_cat_pages_ = PostCategory.select().where(
        PostCategory.category == category
    )

    text = template(
        "include/category-delete.tpl",
        category=category,
        categories=blog.categories.where(Category.id != category.id).order_by(
            Category.title.asc()
        ),
        action_key=action_key,
        c_id=int(c_id),
    )

    if request.method == "POST":

        confirm_key = request.forms.action_key
        if not confirm_key:
            notice.fail("No delete key provided")
        if action_key != confirm_key:
            notice.fail("No delete key provided")

        if notice.is_ok():
            new_category_id = request.forms.new_category
            new_category = Category.get_by_id(new_category_id)

            p: Post
            pp: PostCategory

            partial = True if request.forms.save2 else False

            if partial:
                primary_cat_pages = primary_cat_pages_.limit(25)
                secondary_cat_pages = secondary_cat_pages_.limit(25)

            for p in primary_cat_pages.iterator():
                p.enqueue()
                p.dequeue_post_archives()
                p.queue_erase_post_archive_files()
                p.set_primary_category(new_category)
                p.enqueue()

            for pp in secondary_cat_pages.iterator():
                p = pp.post
                p.enqueue()
                p.dequeue_post_archives()
                p.queue_erase_post_archive_files()
                p.remove_subcategory(category)
                p.add_subcategory(new_category)
                p.enqueue()

            text = f"Category {category.title} deleted and all posts reparented to {new_category.title}. All affected pages pushed to publishing."

            if not partial:
                category.delete_instance()
            else:
                p_count = primary_cat_pages_.count()
                s_count = secondary_cat_pages_.count()
                if p_count == s_count == 0:
                    category.delete_instance()
                else:
                    text = f'Posts reparented from {category.title} to {new_category.title}. <a href="{category.delete_link}?c={new_category.id}">{p_count+s_count} posts left.</a>'

    return template(
        "default.tpl",
        text=text,
        menu=make_menu("blog_category_delete", category),
        blog=blog,
        page_title=f"Delete category {category.title} / {bt_gen(blog)})",
    )


@route("/blog/<blog_id:int>/category/<category_id:int>/posts")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def blog_category_posts(user: User, blog: Blog, category_id: int, search_term=None):
    category: Category
    category = Category.get_by_id(category_id)
    posts_in_cat = category.posts.order_by(Post.date_published.desc())

    if search_term is not None:
        posts_in_cat = blog.search(search_term, posts_in_cat)
        search_button = close_search(category.in_posts_link)
    else:
        search_button = Button(
            "Search", f"{category.in_posts_link}/search?{request.query_string}", "info"
        )

    buttons = make_buttons((search_button,))

    text = format_grid(posts_in_cat, buttons=buttons, search_query=search_term)
    return template(
        "default.tpl",
        text=text,
        menu=make_menu("blog_category_in_posts", category),
        blog=blog,
        search=search_term,
        page_title=f"Posts in category {category.title} / {bt_gen(blog)}",
        request=request,
    )


@route("/blog/<blog_id:int>/category/<category_id:int>/posts/search")
def blog_cat_posts_search(blog_id, category_id):
    search_term = request.query.query
    return blog_category_posts(blog_id, category_id, search_term)


@route("/blog/<blog_id:int>/tags")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def blog_tags(user: User, blog: Blog, search_term=None):

    tags = blog.tags.order_by(Tag.title.asc())
    if search_term is not None:
        tags = Tag.search(search_term, tags)
        menu = make_menu("blog_tags_search", (blog, search_term))
        search_button = close_search(blog.manage_tags_link)
    else:
        menu = make_menu("blog_tags", blog)
        search_button = Button(
            "Search", f"{blog.search_tags_link}?{request.query_string}", "info"
        )

    buttons = make_buttons((search_button,))

    text = format_grid(tags, buttons=buttons, search_query=search_term)
    return template(
        "default.tpl",
        blog=blog,
        text=text,
        search=search_term,
        menu=menu,
        request=request,
        page_title=f"Tags in {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/tags/search")
def blog_tags_search(blog_id):
    search_term = request.query.query
    return blog_tags(blog_id, search_term)


@route("/blog/<blog_id:int>/tag/<tag_id:int>/edit", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def blog_category(user: User, blog: Blog, tag_id: int):
    tag = Tag.get_by_id(tag_id)

    if request.method == "POST":
        tag_title = request.forms.tag_title
        tag_basename = request.forms.tag_basename

        if tag_title != tag.title:
            tag.title = tag_title
            tag.save()

        if tag_basename != tag.basename:
            tag.basename = tag_basename
            tag.verify_basename()
            tag.save()

    text = template("include/tag.tpl", tag=tag)

    return template(
        "default.tpl",
        text=text,
        menu=make_menu("blog_tag", tag),
        blog=blog,
        page_title=f"Tag {tag.title} / {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/tag/<tag_id:int>/posts")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def blog_tags_in_posts(user: User, blog: Blog, tag_id: int, search_term=None):

    tag: Tag
    tag = Tag.get_by_id(tag_id)
    posts = tag.posts.order_by(Post.date_published.desc())
    if search_term is not None:
        posts = blog.search(search_term, posts)
        menu = make_menu("blog_tag_in_posts_search", (tag, search_term))
        search_button = close_search(tag.in_posts_link)
    else:
        menu = make_menu("blog_tag_in_posts", tag)
        search_button = Button(
            "Search", f"{tag.search_posts_link}?{request.query_string}", "info"
        )

    buttons = make_buttons((search_button,))

    text = format_grid(posts, buttons=buttons, search_query=search_term)
    return template(
        "default.tpl",
        blog=blog,
        text=text,
        search=search_term,
        menu=menu,
        page_title=f"Posts in tag {tag.title} / {bt_gen(blog)}",
        request=request,
    )


@route("/blog/<blog_id:int>/tag/<tag_id:int>/posts/search")
def blog_tags_in_posts_search(blog_id, tag_id):
    search_term = request.query.query
    return blog_tags_in_posts(blog_id, tag_id, search_term)


@route("/blog/<blog_id:int>/tag-fetch/<tag_text>")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def blog_tag_fetch(user: User, blog: Blog, tag_text: str):
    results = blog.tags.where(Tag.title ** f"%{tag_text}%")
    result_list = []
    for tag in results:
        result_list.append({"value": tag.title, "id": tag.id})
    return json.dumps(result_list)


@route("/blog/<blog_id:int>/upload", method="POST")
@db_context
@blog_context
@user_context(UserPermission.AUTHOR)
def file_upload(user: User, blog: Blog):
    return file_upload_core(user, blog)


@route("/blog/<blog_id:int>/delete")
@db_context
@blog_context
@user_context(UserPermission.ADMINISTRATOR)
def blog_delete(user: User, blog: Blog):
    blog.delete_instance(recursive=True)
    return "Blog deleted"


@route("/blog/<blog_id:int>/metadata")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def blog_metadata(user: User, blog: Blog):
    return metadata_listing("blog", blog.id, blog, "blog_metadata")


@route("/blog/<blog_id:int>/metadata/<metadata_id:int>/edit", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def blog_metadata_edit(user: User, blog: Blog, metadata_id: int):
    return metadata_edit_(metadata_id, blog, "blog_metadata_edit")


@route("/blog/<blog_id:int>/save-theme", method=("GET", "POST"))
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def blog_export_theme_save(user: User, blog: Blog):
    """
    write current copy of theme to copy in central theme db
    get OK first
    """

    blog.theme.save_copy()

    text = ""

    return template(
        "default.tpl",
        blog=blog,
        text=text,
        menu=make_menu("all_blog_posts", blog),
        page_title=f"Save theme / {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/export-theme")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def blog_export_theme_export(user: User, blog: Blog):
    """
    - save to name
    - export to a theme package file
    - save theme in data directory where it can be applied
    
    """

    blog.theme.export_to_package()
    # if we already have the theme in themes, use that
    # if not, create a temporary zip
    # use the theme save-to-disk function and provide a temp dir to it
    # returns a data stream

    text = ""

    return template(
        "default.tpl",
        blog=blog,
        text=text,
        menu=make_menu("all_blog_posts", blog),
        page_title=f"Export theme / {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/export")
@route("/blog/<blog_id:int>/export/")
@route("/blog/<blog_id:int>/export/<step:int>")
@route("/blog/<blog_id:int>/export/<step:int>/<substep:int>")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def blog_export_theme(user: User, blog: Blog, step=0, substep=1):

    message = ""
    zip_path = pathlib.Path(blog.base_filepath, f"{blog.id}.zip")

    if step == 0:
        archive = zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED,)
        archive.close()
        return redirect(f"/blog/{blog.id}/export/1/1")

    archive = zipfile.ZipFile(zip_path, mode="a", compression=zipfile.ZIP_DEFLATED,)

    if step == 1:
        abs_path = pathlib.Path(blog.base_filepath, "media")
        media_items = blog.media.paginate(substep, 100)
        if media_items.count() == 0:
            return redirect(f"/blog/{blog.id}/export/2")
        message = f"Media items {substep*100} of {blog.media.count()}"
        for media in media_items:
            f_path = pathlib.Path(abs_path, media.full_filepath)
            if f_path.exists():
                archive.write(
                    f_path, f"media/{media.filepath}", compresslevel=zipfile.ZIP_STORED
                )

    elif step == 2:
        posts_json = []
        post_items = blog.posts.paginate(substep, 100)
        if post_items.count() == 0:
            return redirect(f"/blog/{blog.id}/export/3")
        message = f"Posts {substep*100} of {blog.posts.count()}"
        post: Post
        for post in post_items:
            post_dict = model_to_dict(post, recurse=False)
            post_dict["tags"] = post.tags_list
            post_dict["primary_category"] = post.primary_category.title
            post_dict["subcategories"] = [x.title for x in post.subcategories]
            posts_json.append(post_dict)
        archive.writestr(
            f"posts/posts_{substep}.json", json.dumps(posts_json, default=str)
        )

    elif step == 3:
        tags_json = []
        tag_items = blog.tags.paginate(substep, 100)
        if tag_items.count() == 0:
            return redirect(f"/blog/{blog.id}/export/4")
        message = f"Tags {substep*100} of {blog.tags.count()}"
        for tag in tag_items:
            tag_dict = model_to_dict(tag, recurse=False)
            tags_json.append(tag_dict)
        archive.writestr(
            f"tags/tags_{substep}.json", json.dumps(tags_json, default=str)
        )

    elif step == 4:
        categories_json = []
        category_items = blog.categories.paginate(substep, 100)
        if category_items.count() == 0:
            return redirect(f"/blog/{blog.id}/export/-1")
        message = f"Tags {substep*100} of {blog.categories.count()}"
        for category in category_items:
            category_dict = model_to_dict(category, recurse=False)
            categories_json.append(category_dict)
        archive.writestr(
            f"categories/categories_{substep}.json",
            json.dumps(categories_json, default=str),
        )

    # ? users?

    if step != -1:

        archive.close()
        substep += 1

        redir = f"/blog/{blog.id}/export/{step}/{substep}"

        return template(
            "default.tpl",
            text=f"Step {step}/{substep}: {message}",
            headers=f'<meta http-equiv="Refresh" content="0; URL={redir}">',
            blog=blog,
            page_title=f"",
            menu=make_menu("blog_menu", blog),
        )

    archive.close()
    return "Done"
