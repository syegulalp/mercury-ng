from cms.models.enums import QueueStatus, TemplatePublishingMode
from cms.models.models import (
    FileInfoMapping,
    TemplateMapping,
    Template,
    FileInfo,
    UserPermission,
)
from bottle import route, template, request
from cms.models import Blog, Post, User, db_context, Queue, Context
from cms.routes.ui import make_menu
from cms.routes.context import blog_context, user_context, bt_gen

import datetime

# /republish-menu - interface to below options

# /republish - re-queue all existing fileinfos
# /republish-template - re-queue existing fileinfos only for a given template
# /republish-page

# /rebuild - rebuild all fileinfos, give option to queue
# /rebuild-template - rebuild fileinfos for a given template, give option to queue


@route("/blog/<blog_id:int>/republish-options")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def republish_options(user: User, blog: Blog):
    l = blog.manage_link
    text = f"""
<h1>Republishing options</h1><hr>
<ul>
<li><a href="{l}/republish"><b>Republish:</b></a> Iterate through all fileinfos for all pages in the blog, push them into the queue, then run the queue manually.</li>
<li><a href="{l}/runqueue"><b>Run queue manually:</b></a> Iterate through the queue by way of the web interface, rather than the job runner script.</li>
<li><a href="{l}/rebuild-fileinfos"><b>Rebuild fileinfos:</b></a> Delete and recreate all fileinfos for this blog.</li>
<hr/>
<li><a href="{l}/republish-by-page"><b>Republish by page:</b></a> Iterate through all fileinfos for all pages in the blog, push them into the queue, then run the queue manually. Slower than the above republishing option; mainly used for debugging.</li>
</ul>
"""
    return template(
        "default.tpl",
        text=text,
        blog=blog,
        page_title=f"Republishing options for {bt_gen(blog)}",
        menu=make_menu("blog_republish", blog),
    )


@route("/blog/<blog_id:int>/runqueue")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def run_queue(user: User, blog: Blog):

    c_jobs = Queue._control_jobs(blog)
    if (
        c_jobs.where(Queue.status << (QueueStatus.WAITING, QueueStatus.RUNNING)).count()
        > 0
    ):
        return "Queue already running."

    job = c_jobs.where(Queue.status == QueueStatus.MANUAL)
    job_count = job.count()
    if job_count == 0:
        job = Queue.add_control(blog)
    else:
        job = job.get()
    job.lock()

    first_run = False
    p = int(request.query.get("p", 0))

    if p:
        count, timer = Queue.run.__wrapped__(Queue, job, batch_time_limit=2.0)
    else:
        first_run = True
        count = 0
        remaining = (
            Queue.jobs()
            .where(Queue.blog == blog, Queue.date_inserted <= job.date_inserted)
            .count()
        )

    p += 1
    refresh = f'<meta http-equiv="refresh" content="0;url=runqueue?p={p}" />'
    redirect = "<p>Don't navigate away from this page!</p>"

    if not count and not first_run:
        job.delete_instance()
        refresh = ""
        remaining = 0
        redirect = f'<p><a href="{blog.manage_link}">Done. You can now return to blog or close this tab.</a></p>'
        redirect += f"""
<script>
Notification.requestPermission().then(function (permission) {{
      // If the user accepts, let's create a notification
      if (permission === "granted") {{
        var notification = new Notification("Queue run finished for blog {blog.title}");
      }}
}})
</script>
        """
    else:
        job.status = QueueStatus.MANUAL
        job.date_updated = datetime.datetime.utcnow()
        job.save()
        remaining = (
            Queue.jobs()
            .where(Queue.blog == blog, Queue.date_inserted <= job.date_inserted)
            .count()
        )

    return f"""
<html><head>
{refresh}
</head><body>
<p>{count} jobs processed. {remaining} jobs left.</p>
{redirect}
</body></html>
"""


@route("/blog/<blog_id:int>/republish/<pass_:int>")
@route("/blog/<blog_id:int>/republish")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def republish_blog_fast(user: User, blog: Blog, pass_: int = 0):

    all_fileinfos = FileInfo.select()
    all_templates = blog.templates.select(Template.id).where(
        Template.publishing_mode != TemplatePublishingMode.DO_NOT_PUBLISH
    )
    blog_fileinfos = all_fileinfos.where(FileInfo.template << all_templates)
    total_fileinfos = blog_fileinfos.count()

    fileinfos = blog_fileinfos.paginate(pass_, 100)

    text = f"Adding fileinfos {pass_ * 100} of {total_fileinfos}. Don't navigate away"
    redir = f"/blog/{blog.id}/republish/{pass_+1}"
    headers = f'<meta http-equiv="Refresh" content="0; URL={redir}">'

    if fileinfos.count() > 0:
        f: FileInfo
        for f in fileinfos:
            f.enqueue(True)
    else:
        text = "Done."
        headers = ""

    return template(
        "default.tpl",
        text=text,
        headers=headers,
        blog=blog,
        page_title=f"Rebuilding blog #{blog.id}, pass {pass_*100} of {total_fileinfos}",
        menu=make_menu("blog_menu", blog),
    )


@route("/blog/<blog_id:int>/republish-by-page/<pass_:int>")
@route("/blog/<blog_id:int>/republish-by-page")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def republish_blog(user: User, blog: Blog, pass_: int = 0):
    """
    Iterates through all posts in the blog and queues their fileinfos for publication.
    This does not attempt to determine if a given template, newly created, does not yet
    have fileinfos for a given page. It is potentially incomplete if new templates have
    been created without fileinfos created for them.
    """

    post: Post
    p = blog.published_posts.order_by(Post.date_published.asc())

    total_posts = p.count()
    redir = f"/blog/{blog.id}/republish-by-page/{pass_+1}"
    headers = f'<meta http-equiv="Refresh" content="0; URL={redir}">'

    if pass_ == 0:
        text = "Starting republication of blog. Don't navigate away from this page."
    else:
        posts = p.paginate(pass_, 100)
        queue_set = set()
        if posts.count() > 0:
            for post in posts:
                for f in post.fileinfos:
                    queue_set.add(f)
            q: FileInfo
            for q in queue_set:
                q.enqueue()
            text = f"Queued {pass_*100} of {total_posts}... (Don't navigate away yet!)"
        else:
            blog.queue_indexes()
            Queue.start(force_start=True)
            text = "Done. You may now navigate away."
            headers = ""

    return template(
        "default.tpl",
        text=text,
        headers=headers,
        blog=blog,
        page_title=f"Rebuilding blog #{blog.id}, pass {pass_*100} of {total_posts}",
        menu=make_menu("blog_menu", blog),
    )


@route("/blog/<blog_id:int>/rebuild-fileinfos/<pass_:int>")
@route("/blog/<blog_id:int>/rebuild-fileinfos")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def republish_blog_all(user: User, blog: Blog, pass_: int = 0):
    """
    Iterates through all posts in a blog, clears all existing fileinfos, and creates new ones from the available templates. Slow, but complete.
    """

    total_posts = blog.posts.count()
    redir = f"/blog/{blog.id}/rebuild-fileinfos/{pass_+1}"
    headers = f'<meta http-equiv="Refresh" content="0; URL={redir}">'

    if pass_ == 0:
        text = (
            "Starting rebuilding of blog fileinfos. Don't navigate away from this page."
        )

        FileInfo.delete().where(FileInfo.blog == blog).execute()
        fis = FileInfo.select(FileInfo.id)
        FileInfoMapping.delete().where(~FileInfoMapping.fileinfo << fis).execute()
        Context.delete().where(~Context.fileinfo << fis).execute()

    else:
        posts = blog.posts.paginate(pass_, 100)
        if posts.count() > 0:
            post: Post
            for post in posts:
                post.build_fileinfos()
            text = f"Rebuilt {pass_*100} of {total_posts}... (Don't navigate away yet!)"
        else:
            # TODO: rebuild fileinfos for all other template types too
            blog.build_index_fileinfos()
            blog.queue_indexes()
            Queue.start(force_start=True)
            text = "Done. You may now navigate away."
            headers = ""

    return template(
        "default.tpl",
        text=text,
        headers=headers,
        blog=blog,
        page_title=f"Rebuilding fileinfos for blog #{blog.id}, pass {pass_*100} of {total_posts}",
        menu=make_menu("blog_menu", blog),
    )


@route("/blog/<blog_id:int>/create-fileinfos/<template_id:int>/<pass_:int>")
@route("/blog/<blog_id:int>/create-fileinfos/<template_id:int>")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def create_fileinfos_for_template(
    user: User, blog: Blog, template_id: int, pass_: int = 0
):
    """
    Given a template, clears any fileinfos associated with it, then iterates through all posts and generates new fileinfos associated with that template.
    """

    total_posts = blog.published_posts.count()

    headers = ""
    text = ""
    redir = f"/blog/{blog.id}/create-fileinfos/{template_id}/{pass_+1}"

    template_to_republish: Template = Template.get_by_id(template_id)

    if pass_ == 0:
        text = "Starting republication of blog. Don't navigate away from this page."
        mapping: TemplateMapping
        for mapping in template_to_republish.mappings.iterator():
            mapping.clear_fileinfos()
        redir = f"/blog/{blog.id}/create-fileinfos/{template_id}/1"

    else:
        posts = blog.published_posts.paginate(pass_, 100)
        if posts.count() > 0:
            FileInfo.build_fileinfos(
                posts,
                blog,
                [template_to_republish],
                {template_to_republish.id: [_ for _ in template_to_republish.mappings]},
            )
            text = (
                f"Processed {pass_*100} of {total_posts}... (Don't navigate away yet!)"
            )

        else:
            redir = f"/blog/{blog.id}/republish-template/{template_id}"

    if redir:
        headers = f'<meta http-equiv="Refresh" content="0; URL={redir}">'

    return template(
        "default.tpl",
        text=text,
        headers=headers,
        blog=blog,
        page_title=f"Rebuilding blog #{blog.id}, pass {pass_*100} of {total_posts}",
        menu=make_menu("blog_menu", blog),
    )


@route("/blog/<blog_id:int>/republish-template/<template_id:int>/<pass_:int>")
@route("/blog/<blog_id:int>/republish-template/<template_id:int>")
@db_context
@blog_context
@user_context(UserPermission.EDITOR)
def republish_template(user: User, blog: Blog, template_id: int, pass_: int = 0):
    """
    Given a template, iterates through all live fileinfos for that template and queues them for publication.
    """

    posts = blog.published_posts.select(Post.id)
    live_mappings = FileInfoMapping.select(FileInfoMapping.fileinfo).where(
        FileInfoMapping.post << posts
    )
    published_fileinfos = FileInfo.select(FileInfo.id).where(
        FileInfo.id << live_mappings
    )
    template_to_republish: Template = Template.get_by_id(template_id)
    total_fileinfos = template_to_republish.fileinfos.where(
        FileInfo.id << published_fileinfos
    )

    text = ""
    headers = ""
    redir = f"/blog/{blog.id}/republish-template/{template_id}/{pass_+1}"

    if pass_ == 0:
        text = "Starting republication of template. Don't navigate away from this page."

    else:
        fileinfos = total_fileinfos.paginate(pass_, 100)
        if fileinfos.count() > 0:
            fileinfo: FileInfo
            for fileinfo in fileinfos:
                fileinfo.enqueue()
            text = f"Queued {pass_*100} of {total_fileinfos.count()}... (Don't navigate away yet!)"
        else:
            Queue.start(force_start=True)
            redir = f"{blog.manage_link}/runqueue"
            text = "Done. Switching to manual queue runner."

    if redir:
        headers = f'<meta http-equiv="Refresh" content="0; URL={redir}">'

    return template(
        "default.tpl",
        text=text,
        headers=headers,
        blog=blog,
        page_title=f"Rebuilding blog #{blog.id}, pass {pass_*100} of {total_fileinfos.count()}",
        menu=make_menu("blog_menu", blog),
    )
