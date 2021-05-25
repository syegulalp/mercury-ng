import pathlib

# attempt to import existing settings

try:
    from data.settings import *

except ImportError:

    # Check if the settings directory even exists.
    # If not, create it and populate it.

    DATA_PATH = pathlib.Path("data")

    if not DATA_PATH.exists():
        DATA_PATH.mkdir()
        with open(pathlib.Path(DATA_PATH, "__init__.py"), "w") as f:
            f.write("")
        import os

        with open(pathlib.Path(DATA_PATH, "settings.py"), "w") as f:
            f.write(
                f"# Auto-generated salt for hashing passwords. DO NOT CHANGE THIS VALUE!\nSALT = {os.urandom(32)}\n"
            )

    from data.settings import *

l = locals()
import os

app_dir = os.path.dirname(__file__)

DATA_PATH = l.get("DATA_PATH", pathlib.Path("data"))
DATABASE_PATH = l.get("DATABASE_PATH", pathlib.Path(DATA_PATH, "database.cgi"))

APP_URL = l.get("APP_URL", "")
APP_DIR = l.get("APP_DIR", app_dir)

MAINTENANCE_MODE = l.get("MAINTENANCE_MODE", False)

DEBUG = l.get("DEBUG", False)

# constants

PRODUCT_NAME = "Mercury"
PRODUCT_VERSION = "0.0.2"
