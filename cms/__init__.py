import regex as re

from . import settings

import pathlib

import bottle

bottle.DEBUG = settings.DEBUG
bottle.re = re
bottle.TEMPLATE_PATH.insert(0, str(pathlib.Path(settings.APP_DIR, "views")))
run_app = bottle.run

import peewee

peewee.re = re

# First app boot check

if not settings.DATABASE_PATH.exists():
    from . import setup

    setup.create_database()

# Determine if we're in the setup phase

from .models import Metadata, LoginTokens, db

db.connect()
try:
    setup_step = Metadata.get(object_name="_system", key="setup_step")
    settings.SETUP_IN_PROGRESS = True
except Metadata.DoesNotExist:
    settings.SETUP_IN_PROGRESS = False

# Remove any expired tokens

LoginTokens.clear_expired()

import sys

if "--setup" in sys.argv[1:]:
    from .routes import setup

    setup.create_first_blog()
    setup.initialize_first_blog()
    setup.leave_setup_mode()
    sys.exit()

from .routes import app

db.close()
