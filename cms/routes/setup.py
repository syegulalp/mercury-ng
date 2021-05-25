from bottle import route, template, request, redirect
from ..models import (
    Blog,
    Metadata,
    Theme,
    User,
    Category,
    Post,
    PublicationStatus,
    Queue,
    db_context,
)
from .. import settings
import pathlib

setup_text = {
    0: "Welcome to your blog's setup",
    1: "Your blog's name and description",
    2: "Your blog's URL and path",
    3: "Confirm your settings",
    4: "You're done!",
}


@db_context
@route("/setup", method=("GET", "POST"))
@route("/setup/<step_id:int>", method=("GET", "POST"))
def setup_step(step_id: int = 0):
    method = "_post" if request.method == "POST" else ""
    stepfunc = globals().get(f"step_{step_id}{method}")
    return stepfunc(step_id)


def step_0(step_id):
    return template("setup/step_0.tpl", step_id=step_id, setup_text=setup_text)


def create_first_blog():
    return Blog.create(
        title="Your first blog",
        description="The first blog you've created in your new installation.",
        base_url="https://your.url",
        base_filepath="output",
    )


def step_1(step_id):
    try:
        first_blog = Blog.get_by_id(1)
    except:
        first_blog = create_first_blog()

    return template(
        "setup/step_1.tpl",
        step_id=step_id,
        blog=first_blog,
        tab="",
        setup_text=setup_text,
    )


def step_1_post(step_id):
    first_blog = Blog.get_by_id(1)
    first_blog.title = request.forms.blog_title
    first_blog.description = request.forms.blog_description
    return redirect("/setup/2")


def step_2(step_id):
    first_blog = Blog.get_by_id(1)

    return template(
        "setup/step_1.tpl",
        step_id=step_id,
        blog=first_blog,
        tab="url",
        setup=True,
        setup_text=setup_text,
    )


def step_2_post(step_id):
    first_blog = Blog.get_by_id(1)
    first_blog.base_url = request.forms.base_url
    first_blog.base_filepath = request.forms.base_filepath

    first_blog.save()

    if "refresh" in request.forms:
        return step_2(step_id)

    return redirect("/setup/3")


def step_3(step_id):
    first_blog = Blog.get_by_id(1)

    return template(
        "setup/confirm.tpl", step_id=step_id, blog=first_blog, setup_text=setup_text
    )


def leave_setup_mode():
    setup_step = Metadata.get(object_name="_system", key="setup_step")
    setup_step.delete_instance()
    settings.SETUP_IN_PROGRESS = False


def step_4(step_id):
    first_blog: Blog = Blog.get_by_id(1)

    blog_file_path: pathlib.Path = pathlib.Path(first_blog.base_filepath)

    if not blog_file_path.exists():
        blog_file_path.mkdir()

    initialize_first_blog()
    leave_setup_mode()

    return template("setup/finished.tpl", step_id=step_id, setup_text=setup_text)


def initialize_first_blog():

    theme = Theme.install_theme()
    user = User.get_by_id(1)
    new_blog: Blog = Blog.get_by_id(1)

    new_blog.apply_theme(theme)
    new_blog.build_index_fileinfos()

    new_category = Category.create(
        title="Uncategorized", description="", basename="blog", blog=new_blog
    )

    new_blog_post = Post.create(
        title="Welcome to your new blog!",
        text="Write content here.",
        blog=new_blog,
        author=user,
        status=PublicationStatus.PUBLISHED,
        basename="",
    )

    new_blog_post.basename = new_blog_post.create_basename()
    new_blog_post.save()

    new_blog_post.build_fileinfos()
    new_blog_post.enqueue()
    Queue.run_immediately(new_blog)
