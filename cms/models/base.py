from cms.db import db

from peewee import Model, IntegerField, TextField, CharField, OperationalError

from cms.models.utils import unsafe
from time import perf_counter as clock
from cms import settings


class MetadataModel:
    def get_metadata(self, key=None, obj_name=None, obj_id=None):
        if not obj_name:
            obj_name = self._meta.table_name
        if not obj_id:
            obj_id = self.id
        try:
            get_key = Metadata.select().where(
                Metadata.object_name == obj_name, Metadata.object_id == obj_id,
            )
            if key:
                get_key = get_key.where(Metadata.key == key).get()

        except Exception as e:
            return None
        else:
            return get_key

    def set_metadata(self, key, value):
        key_value = self.get_metadata(key)
        if key_value is None:
            key_value = Metadata(
                object_name=self._meta.table_name,
                object_id=self.id,
                key=key,
                value=value,
            )
        key_value.value = value
        key_value.save()

    def del_metadata(self, key):
        key_value = self.get_metadata(key)
        if key_value is not None:
            Metadata.get(id=key_value.id).delete_instance()

    def delete_instance(self, *a, **ka):
        Metadata.delete().where(
            Metadata.object_name == self._meta.table_name, Metadata.object_id == self.id
        ).execute()
        super().delete_instance(*a, **ka)


class BaseModel(Model, MetadataModel):
    class Meta:
        database = db

    @property
    def manage_link(self):
        raise NotImplementedError

    @property
    def manage_link_html(self):
        return f'<a href="{self.manage_link}">{self.title_for_listing}</a>'

    @property
    def title_for_listing(self):
        return f"<b>{unsafe(self.title)}</b>"

    @property
    def title_for_display(self):
        return f"<b>{unsafe(self.title)} (#{self.id})</b>"

    @property
    def title_with_id(self):
        return f"{self.title} (#{self.id})"

    @classmethod
    def display(cls, query):
        pass

    @classmethod
    def listing_columns(cls):
        raise NotImplementedError

    def listing(self):
        raise NotImplementedError

    # Legacy ID reverse search.
    # Eventually we can discard this.

    legacy_values = {}

    @classmethod
    def get_legacy(cls, value):
        if value is None:
            return None
        return BaseModel.legacy_values[(cls._meta.table_name, value)]

    def set_legacy(self, value):
        BaseModel.legacy_values[(self._meta.table_name, value)] = self.id


class OtherModel:
    pass


class Metadata(BaseModel):
    object_name = CharField(null=False, index=True)
    object_id = IntegerField(null=False, index=True)
    key = TextField(null=False, index=True)
    value = TextField(null=True)

    @classmethod
    def listing_columns(cls):
        return "ID", "Object", "", "Key", "Value"

    def listing(self):
        return (
            self.id,
            self.object_name,
            self.object_id,
            f'<a href="metadata/{self.id}/edit">{self.key}</a>',
            self.value,
        )


def db_context(func):
    def wrapper(*a, **ka):
        if settings.MAINTENANCE_MODE:
            return "System is currently in maintenance mode. Try again shortly."
        start = clock()
        db.connect(True)
        while True:
            try:
                with db.atomic():
                    result = func(*a, **ka)
            except OperationalError as e:
                if clock() - start > 30.0:
                    db.close()
                    raise e
                continue
            except Exception as e:
                db.close()
                raise e
            else:
                db.close()
                return result

    wrapper.__wrapped__ = func
    return wrapper
