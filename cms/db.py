import pathlib
from cms import settings

from playhouse.sqlite_ext import SqliteExtDatabase as DBTYPE

db = DBTYPE(
    pathlib.Path(settings.DATABASE_PATH),
    timeout=60,
    pragmas=(
        ("encoding", "'utf-8'"),
        ("cache_size", -1024 * 64),
        ("journal_mode", "wal"),
        ("synchronous", 0),
        ("temp_store", "MEMORY")
    ),
)
