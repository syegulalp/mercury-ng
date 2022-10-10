from cms.models.utils import hash_password
from bottle import (
    route,
    template,
    static_file,
    response,
    redirect,
    request,
    HTTPResponse,
)
from cms.routes.ui import make_menu, make_buttons, format_grid, Button, Notice, Tab
from cms.routes.context import user_context, system_context
from cms.models import (
    User,
    Blog,
    Theme,
    db_context,
    db,
    Queue,
    System,
    UserPermission,
    Metadata,
)
from cms.settings import PRODUCT_NAME, APP_DIR
from cms import settings
from cms.errors import UserNotLoggedIn
import pathlib
import hashlib


USERS_TABS = {
    "name": Tab("Name/Email", "/user/{tabitem.id}"),
    "password": Tab("Password", "/user/{tabitem.id}/password"),
    "permissions": Tab("Permissions", "/user/{tabitem.id}/permissions"),
    "unlock": Tab("Unlock", "/user/{tabitem.id}/unlock"),
}

ME_TABS = {
    "name": Tab("Name/Email", "/me"),
    "password": Tab("Password", "/me/password"),
    "unlock": Tab("Unlock", "/me/unlock"),
}


@route("/reboot")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def reboot(user, system):
    yield ("Shutdown.")
    db.close()
    import os, signal

    os.kill(os.getpid(), signal.SIGTERM)


@route("/")
@db_context
@user_context()
def system_menu(user):
    homepage = template("include/homepage.tpl", user=user)
    return template(
        "default.tpl",
        text=homepage,
        menu=make_menu("system_menu"),
        page_title=f"{PRODUCT_NAME}",
        system=System,
    )


@route("/clean")
def clean():
    db.connect(True)
    settings.MAINTENANCE_MODE = True
    db.execute_sql("VACUUM")
    db.commit()
    settings.MAINTENANCE_MODE = False
    db.close()
    return "Done"


@route("/static/<filepath:path>")
def static_content(filepath):
    r = static_file(filepath, root=pathlib.Path(APP_DIR, "static"))
    r.headers["Cache-Control"] = "max-age=86400"
    return r


@route("/login", method=("GET", "POST"))
@db_context
def login_menu():
    notice = Notice()
    try:
        token = request.get_cookie("token")
        user = User.get_by_token(token)
    except UserNotLoggedIn:
        user = None
    if request.method == "POST":
        email = request.forms.email
        pwd = request.forms.password
        pwd_hash = hash_password(pwd).hex()
        try:
            user = User.get(email=email, password=pwd_hash)
        except User.DoesNotExist:
            notice.fail("Wrong username or password")
        else:
            token = user.create_token()
            response.set_cookie("token", token, path="/")

    return template("login.tpl", settings=settings, notice=notice, user=user)


@route("/logout", method=("GET", "POST"))
@db_context
@user_context()
def logout(user):
    token = request.get_cookie("token")
    user.clear_token(token)
    return "logged out"


@route("/system/info")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def system_info(user, system):
    return template(
        "default.tpl",
        text="Hello world",
        menu=make_menu("system_menu"),
        page_title=f"System info ({PRODUCT_NAME})",
        system=system,
    )


@route("/system/log")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def system_log(user, system):
    return template(
        "default.tpl",
        text="Hello world",
        menu=make_menu("system_menu"),
        page_title=f"System activity log ({PRODUCT_NAME})",
        system=system,
    )


@route("/blogs")
@db_context
@system_context
@user_context()
def blogs_menu(user: User, system):
    blogs = Blog.select()
    buttons = make_buttons((Button("Create new blog", Blog.create_link),))
    text = format_grid(blogs, buttons=buttons)

    return template(
        "default.tpl",
        text=text,
        menu=make_menu("blogs_menu"),
        page_title=f"All blogs ({PRODUCT_NAME})",
        system=system,
    )


@route("/themes")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def themes_menu(user: User, system):
    themes = Theme.select()
    text = format_grid(themes)

    return template(
        "default.tpl",
        text=text,
        menu=make_menu("system_themes"),
        page_title=f"All themes ({PRODUCT_NAME})",
        system=system,
    )


@route("/theme/<theme_id:int>")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def theme_view(user: User, system, theme_id: int):
    theme = Theme.get(id=theme_id)

    return template(
        "default.tpl",
        text=template("include/theme-info.tpl", theme=theme),
        menu=make_menu("system_theme", theme),
        page_title=f"Theme #{theme.id} ({PRODUCT_NAME})",
        system=system,
    )


@route("/theme/<theme_id:int>/export/<filename>")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def themes_menu(user: User, system, theme_id: int, filename: str):

    theme: Theme = Theme.get(id=theme_id)
    return HTTPResponse(theme.as_archive(), content_type="archive/zip")


@route("/users")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def users_menu(user: User, system):
    users = User.select()
    text = format_grid(users)

    return template(
        "default.tpl",
        text=text,
        menu=make_menu("system_users"),
        page_title=f"All users ({PRODUCT_NAME})",
        system=system,
    )


@route("/user/<user_id:int>", method=("GET", "POST"))
@route("/user/<user_id:int>/<tab>", method=("GET", "POST"))
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def user_view(user: User, system, user_id: int, tab="name"):
    return users_menu_base(user, system, user_id, tab)


def users_menu_base(user: User, system, user_id: int, tab="name", tabs=USERS_TABS):

    viewed_user: User = User.get_by_id(user_id)
    notice = Notice()

    # ToDO: not ideal way to verify permissions

    if tabs is ME_TABS:
        menu = make_menu("user_me", context=user)
        admin = False
    else:
        menu = make_menu("system_user", context=viewed_user)
        admin = True

    if tab == "permissions":
        if not admin:
            return redirect("/me")

    if request.method == "POST":
        try:
            if tab == "name":
                viewed_user.change_name(request.forms.user_name)
                viewed_user.change_email(request.forms.user_email)
            elif tab == "password":
                if request.forms.user_password != request.forms.user_password_verify:
                    raise Exception("Passwords do not match.")
                else:
                    viewed_user.change_password(request.forms.user_password)
            elif tab == "permissions":
                pass
                # if add, add, but don't add if exists
                # if remove, except if you're trying to remove your own admin bit
        except Exception as e:
            notice.fail(e)
        else:
            notice.ok("User details saved.")

    text = template(
        "include/user.tpl", user=viewed_user, editable=True, tab=tab, admin=admin
    )

    return template(
        "default.tpl",
        text=text,
        menu=menu,
        page_title=f"User {user.name} (#{user.id}) ({PRODUCT_NAME})",
        system=system,
        notice=notice,
        tabs=tabs,
        tabitem=viewed_user,
        tab=tab,
    )


@route("/new-blog", method=("GET", "POST"))
def new_blog():
    redir, response = new_blog_base()
    if redir:
        return redirect(redir)
    else:
        return response


@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def new_blog_base(user: User, system):

    redir = ""
    notice = Notice()

    blog = Blog(title="", description="", base_filepath=".", base_url="http://my.url")

    if request.method == "POST":

        blog.title = request.forms.blog_title
        blog.description = request.forms.blog_description
        blog.base_filepath = request.forms.base_filepath
        blog.base_url = request.forms.base_url

        if "submit" in request.forms:
            if notice.is_ok:
                blog.save()
                blog.apply_theme(Theme.get_by_id(1))
                blog.create_category("Uncategorized / General", "", "blog")
                Queue.run_queue_(blog)
                return blog.manage_link, None

    # TODO: push to queue, then redirect to queue builder.
    # Don't build here.

    text1 = template(
        "include/blog-settings.tpl",
        blog=blog,
        tab="",
        no_form=True,
        no_button=True,
        setup=True,
    )

    text2 = template(
        "include/blog-settings.tpl",
        blog=blog,
        tab="url",
        no_form=True,
        setup=True,
    )

    return (
        redir,
        template(
            "default.tpl",
            text=f'<h2>Create new blog</h2><form method="post">{text1}<hr/>{text2}</form>',
            menu=make_menu("blogs_menu"),
            page_title=f"Creating new blog",
            system=system,
            notice=notice,
        ),
    )


@route("/metadata")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def system_metadata(user: User, system):
    return metadata_listing("_system", system.id, system, "system_metadata")


@route("/new-metadata", method=("GET", "POST"))
def metadata_new():
    redir, response = metadata_new_()
    if redir:
        return redirect(redir)
    else:
        return response


@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def metadata_new_(user: User, system):
    metadata = Metadata()
    metadata.object_name = "_system"
    metadata.object_id = "0"
    metadata.key = ""
    metadata.value = ""
    notice = Notice()

    text = template("include/metadata.tpl", metadata=metadata)

    if request.method == "POST":
        metadata.key = request.forms.metadata_key
        metadata.value = request.forms.metadata_value

        text = template("include/metadata.tpl", metadata=metadata)

        if metadata.key == "" or metadata.key is None:
            notice.fail("Key cannot be empty")

        if notice.is_ok():
            metadata.save()
            return (f"/metadata/{metadata.id}/edit", "")

    return (
        None,
        template(
            "default.tpl",
            text=text,
            menu=make_menu("system_metadata_new", (metadata, system)),
            page_title=f"All blogs ({PRODUCT_NAME})",
            blog=system,
            notice=notice,
        ),
    )


@route("/metadata/<metadata_id:int>/edit", method=("GET", "POST"))
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def metadata_edit(user: User, system, metadata_id: int):
    return metadata_edit_core(metadata_id, system, "system_metadata_edit")


def metadata_listing(object_type, object_id, context, menu):
    metadata = Metadata.select().where(
        Metadata.object_name == object_type, Metadata.object_id == object_id
    )
    buttons = make_buttons((Button("Create new metadata", "/new-metadata"),))
    text = format_grid(metadata, buttons=buttons)

    return template(
        "default.tpl",
        text=text,
        menu=make_menu(menu, context),
        page_title=f"All blogs ({PRODUCT_NAME})",
        blog=context,
    )


def metadata_edit_core(metadata_id, context, menu):
    metadata = Metadata.get_by_id(metadata_id)
    notice = Notice()

    if request.method == "POST":
        if request.forms.delete:
            # TODO: move all hashlib confirmations to the schema
            confirmation = hashlib.sha256(str(metadata.id).encode("utf-8")).hexdigest()
            notice.warning(
                f"Are you sure you want to delete this metadata?",
                f"/metadata/{metadata.id}/delete",
                confirmation,
                f"/metadata/{metadata.id}/edit",
            )
        else:
            metadata.key = request.forms.metadata_key
            metadata.value = request.forms.metadata_value
            notice.ok("Changes saved")
            metadata.save()

    text = template("include/metadata.tpl", metadata=metadata)

    return template(
        "default.tpl",
        text=text,
        menu=make_menu(menu, (metadata, context)),
        page_title=f"All blogs ({PRODUCT_NAME})",
        blog=context,
        notice=notice,
    )


@route("/metadata/<metadata_id:int>/delete", method="POST")
@db_context
@system_context
@user_context(UserPermission.ADMINISTRATOR)
def metadata_delete(user: User, system, metadata_id: int):
    metadata = Metadata.get_by_id(metadata_id)
    notice = Notice()
    confirmation = hashlib.sha256(str(metadata.id).encode("utf-8")).hexdigest()
    if confirmation == request.forms.action_key:
        metadata.delete_instance()
        notice.ok(f"Metadata #{metadata.id} deleted")

    return template(
        "default.tpl",
        text="",
        menu=make_menu("system_metadata_edit", (metadata, system)),
        page_title=f"All blogs ({PRODUCT_NAME})",
        blog=system,
        notice=notice,
    )
