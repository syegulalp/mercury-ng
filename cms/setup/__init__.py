# Paths and helpers for setup process, which is initiated if either no database is detected or the DB has a setup step meta in it

in_progress = False


def create_database():
    from cms.models.enums import UserPermission
    from cms import models
    from cms.db import db
    import datetime

    all_tables = [_ for _ in models.BaseModel.__subclasses__()] + [
        _ for _ in models.OtherModel.__subclasses__()
    ]

    db.drop_tables(all_tables)
    db.create_tables(all_tables)

    models.Metadata.create(object_name="_system", object_id=0, key="schema_id", value=0)
    models.Metadata.create(
        object_name="_system", object_id=0, key="setup_step", value=0
    )

    admin_user = models.User(
        name="Admin",
        email="admin@bogus.com",
        password=models.utils.hash_password("password").hex(),
        last_login=datetime.datetime.utcnow(),
    )
    admin_user.save()
    admin_user.add_permission(0, UserPermission.ADMINISTRATOR)
    db.close()
