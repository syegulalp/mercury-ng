from peewee import IntegerField
from .enums import (
    PublicationStatus,
    TemplateType,
    TemplatePublishingMode,
    QueueObjType,
    QueueStatus,
    UserPermission,
)


class PubStatusField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return PublicationStatus(value)


class TemplateTypeField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return TemplateType(value)


class PublishingModeField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return TemplatePublishingMode(value)


class QueueObjTypeField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return QueueObjType(value)


class QueueStatusField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return None if value is None else QueueStatus(value)


class PermissionField(IntegerField):
    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return UserPermission(value)
