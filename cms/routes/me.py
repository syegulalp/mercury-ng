from bottle import route, template, request
from ..models import User, db_context, Post, UserPermission, System
from .ui import format_grid, make_menu, make_buttons, Button, Notice
from .context import user_context, bt_gen, system_context
from .system import users_menu_base, ME_TABS

import hashlib


@route("/me", method=("GET", "POST"))
@route("/me/<tab>", method=("GET", "POST"))
@db_context
@user_context()
def user_self_menu(user: User, tab="name"):
    return users_menu_base(user, System, user_id=user.id, tab=tab, tabs=ME_TABS)


@route("/me/unlock")
@db_context
@system_context
@user_context()
def unlock_articles(user: User, system):

    posts = (
        Post.select()
        .where(Post.open_for_editing_by == user)
        .order_by(Post.date_published.desc())
    )

    buttons = make_buttons((Button("Unlock all", "/me/unlock-all"),))

    text = format_grid(posts, buttons=buttons)
    return template(
        "default.tpl",
        blog=system,
        text=text,
        menu=make_menu("unlock_menu", context=user),
        page_title=bt_gen(system),
    )


@route("/me/unlock-all", method=("GET", "POST"))
@db_context
@system_context
@user_context()
def unlock_articles_confirm(user: User, system):

    notice = Notice()

    confirmation = hashlib.sha256(
        user.name.encode("utf-8") + str(user.id).encode("utf-8")
    ).hexdigest()

    if request.method == "GET":
        notice.warning(
            f"Are you sure you want to release edit locks on all your blog posts?",
            "unlock-all",
            confirmation,
            "/me/unlock",
        )

    else:

        confirm_key = request.forms.action_key

        if confirm_key == confirmation:
            Post.update(open_for_editing_by=None).where(
                Post.open_for_editing_by == user
            ).execute()
            notice.ok(f"All edit locks released.")
        else:
            notice.fail("No unlock key provided")

    return template(
        "default.tpl",
        menu=make_menu("blogs_menu"),
        page_title=f"Unlocking posts / {bt_gen(system)}",
        notice=notice,
        text="",
        blog=system,
    )
