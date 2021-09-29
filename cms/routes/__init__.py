from bottle import default_app, error, HTTPError
from . import context, setup, system, blog, post, template, media, queue, republish, me
from cms.errors import BlogPermissionError
from cms.models import unsafe


@error(500)
def error500(error):
    if isinstance(error.exception, BlogPermissionError):
        return "You don't have permission to access that resource"
    elif isinstance(error, HTTPError):
        return f"<pre>{unsafe(str(error.traceback))}</pre>"    
    return f"<pre>{unsafe(str(error))}</pre>"


app = default_app()
