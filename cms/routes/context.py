from cms.models.models import Permission
from bottle import template, request, redirect
from cms.models import User, Blog, Template, Post, Metadata, db, System, UserPermission
from cms import settings
from cms.errors import UserNotLoggedIn, BlogPermissionError


def bt_gen(blog):
    return f"{blog.title} (#{blog.id}) ({settings.PRODUCT_NAME})"


def user_context(permission=None):
    def decorator(func):
        def wrapper(*a, **ka):
            if getattr(settings, "SETUP_IN_PROGRESS"):
                setup_step = Metadata.get(object_name="_system", key="setup_step")
                return redirect(f"/setup/{setup_step.value}")

            try:
                token = request.get_cookie("token")
                user = User.get_by_token(token)
            except UserNotLoggedIn:
                return redirect("/login")

            if permission is not None:
                # Sitewide
                if not (0, UserPermission.ADMINISTRATOR) in user.permissions:
                    a1 = a[0]
                    id = a1.id if a1 is System or isinstance(a1, Blog) else a1.blog.id
                    if not (id, permission) in user.permissions:
                        raise BlogPermissionError()

            return func(user, *a, **ka)

        return wrapper

    return decorator


def blog_context(func):
    def wrapper(blog_id, *a, **ka):
        try:
            blog = Blog.get_by_id(blog_id)
        except Blog.DoesNotExist as e:
            return template("error.tpl", error=e)
        return func(blog, *a, **ka)

    return wrapper


def template_context(func):
    def wrapper(template_id, *a, **ka):
        try:
            tpl = Template.get_by_id(template_id)
        except Template.DoesNotExist as e:
            return template("error.tpl", error=e)
        return func(tpl, *a, **ka)

    return wrapper


def post_context(func):
    def wrapper(blog_id, post_id, *a, **ka):
        try:
            post = Post.get(id=post_id, blog_id=blog_id)
        except Post.DoesNotExist as e:
            return template("error.tpl", error=e)
        return func(post, *a, **ka)

    return wrapper


def system_context(func):
    def wrapper(*a, **ka):
        return func(System, *a, **ka)

    return wrapper
