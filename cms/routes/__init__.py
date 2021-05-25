from bottle import default_app, error
from . import context, setup, system, blog, post, template, media, queue, republish, me
from ..errors import BlogPermissionError
from ..models import unsafe


@error(500)
def error500(error):
    if isinstance(error.exception, BlogPermissionError):
        return "You don't have permission to access that resource"
    return f"<pre>{unsafe(str(error))}</pre>"


app = default_app()
