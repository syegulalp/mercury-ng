from cms.models.enums import QueueStatus, UserPermission
from bottle import route, template
from ..models import Blog, User, db_context, Queue
from .ui import format_grid, make_menu, make_buttons, Notice, Button
from .context import blog_context, user_context, bt_gen

from ..settings import PRODUCT_NAME
import datetime


@route("/blog/<blog_id:int>/queue")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def blog_queue(user: User, blog: Blog):
    queue = blog.queue_items

    notice = Notice()

    # TODO:
    # use this header in both queue contexts

    if Queue.is_locked(blog):
        restart_button = Button(
            "Stop queue", f"{blog.queue_manage_link}/stop", "danger"
        )
        if Queue.control_jobs(
            blog
        ).date_updated < datetime.datetime.now() - datetime.timedelta(seconds=10):
            notice.fail(
                f"Queue is marked as currently running, but the last update to the queue was more than 10 seconds ago. The queue process may have failed, or may be stuck on a particularly long-running job. (<a href='{blog.queue_manage_link}/run'>Restart)</a>"
            )
        else:
            notice.notice(
                f"Queue is currently running for this blog with <b>{queue.count()}</b> items remaining. (<a href='queue'>Refresh</a>)"
            )
    else:
        restart_button = Button(
            "Restart queue", f"{blog.queue_manage_link}/run", "warning"
        )
        if queue.count():
            if Queue.failures(blog):
                notice.fail(
                    f"Queue has failed jobs pending. (<a href='{blog.queue_manage_link}/reset-failed'>Reset jobs)</a>"
                )
            else:
                notice.notice(
                    f"Queue is not currently running but has pending jobs. (<a href='{blog.queue_manage_link}/run'>Restart)</a>"
                )
        else:
            notice.ok("Queue has no jobs and is not currently running.")

    buttons = make_buttons(
        (
            Button("Clear queue", f"{blog.queue_manage_link}/clear"),
            restart_button,
            Button(
                "Reset failed jobs",
                f"{blog.queue_manage_link}/reset-failed",
                "secondary",
            ),
        )
    )
    text = format_grid(queue, buttons=buttons)

    return template(
        "default.tpl",
        blog=blog,
        text=text,
        notice=notice,
        menu=make_menu("blog_queue", blog),
        page_title=f"Publishing queue for {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/queue/<action>")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def blog_clear_queue(user: User, blog: Blog, action: str):

    # TODO: protect against clickjack

    notice = Notice()

    if action == "clear":
        Queue.delete().where(Queue.blog == blog).execute()
        notice.ok("Blog queue cleared.")
    elif action == "stop":
        Queue.stop(blog)
        notice.ok("Blog queue publishing stopped.")
    elif action == "run":
        Queue.restart(blog)
        notice.ok("Blog queue publishing started.")
    elif action == "reset-failed":
        Queue.reset_failed(blog)
        # force start
        Queue.start(force_start=True)
        notice.ok("Resetting failed jobs.")

    notice.ok(f'<a href="{blog.queue_manage_link}">Click here to return to queue.</a>')

    return template(
        "default.tpl",
        blog=blog,
        text="",
        notice=notice,
        menu=make_menu("blog_menu", blog),
        page_title=f"Publishing queue for {bt_gen(blog)}",
    )


@route("/blog/<blog_id:int>/queue-item/<item_id:int>")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def blog_queue_item(user: User, blog: Blog, item_id: int):

    queue_item = Queue.get_by_id(item_id)

    text = f"<pre>{queue_item.failure_data}<pre>"

    return template(
        "default.tpl",
        blog=blog,
        text=text,
        menu=make_menu("blog_menu", blog),
        page_title=f"Item # {item_id} in publishing queue for {bt_gen(blog)}",
    )
