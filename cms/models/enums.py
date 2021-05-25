from enum import Enum


class PublicationStatus(Enum):
    DRAFT = 0
    # Not published
    SCHEDULED = 1
    # Scheduled for publication
    PUBLISHED = 2
    # Live
    SPIKED = 3
    # Not to be published; cannot be changed except by an editor

    def __repr__(self):
        return str(self)


PublicationStatus.txt = {x: x.name.lower().capitalize() for x in PublicationStatus}


class Actions:
    class Draft:
        SAVE_DRAFT = "Save draft"
        SAVE_AND_SCHEDULE = "Save and schedule"
        SAVE_AND_PUBLISH_NOW = "Save and publish now"

    class Preview:
        PREVIEW_ONLY = "Preview only (no save)"
        SAVE_AND_PREVIEW = "Save & preview"

    class Scheduled:
        SAVE_DRAFT = "Save draft"
        SAVE_AND_UNSCHEDULE = "Save and unschedule"
        SAVE_AND_PUBLISH_NOW = "Save and publish now"

    class Published:
        SAVE_DRAFT_ONLY = "Save to draft only"
        SAVE_AND_UPDATE_LIVE = "Save and update live"
        UNPUBLISH = "Unpublish"

    CLOSE = "Close and release edit lock"


editor_actions = {
    PublicationStatus.DRAFT: (
        Actions.Draft.SAVE_DRAFT,
        Actions.Draft.SAVE_AND_SCHEDULE,
        Actions.Draft.SAVE_AND_PUBLISH_NOW,
    ),
    PublicationStatus.SCHEDULED: (
        Actions.Scheduled.SAVE_DRAFT,
        Actions.Scheduled.SAVE_AND_UNSCHEDULE,
        Actions.Scheduled.SAVE_AND_PUBLISH_NOW,
    ),
    PublicationStatus.PUBLISHED: (
        Actions.Published.SAVE_DRAFT_ONLY,
        Actions.Published.SAVE_AND_UPDATE_LIVE,
        Actions.Published.UNPUBLISH,
    ),
    PublicationStatus.SPIKED: ("Nothing"),
}

editor_button_colors = {
    PublicationStatus.DRAFT: "warning",
    PublicationStatus.SCHEDULED: "primary",
    PublicationStatus.PUBLISHED: "success",
    PublicationStatus.SPIKED: "danger",
}


class UserPermission(Enum):
    AUTHOR = 0
    # Can create and schedule posts
    EDITOR = 1
    # Can modify posts not written by them
    DESIGNER = 2
    # Can modify templates and posts
    ADMINISTRATOR = 3
    # can modify everything


class TemplateType(Enum):
    INDEX = 0
    ARCHIVE = 1
    POST = 2
    INCLUDE = 3
    SSI = 4
    CODE = 5
    MEDIA = 6
    SYSTEM = 7


TemplateType.txt = {x: x.name.lower().capitalize() for x in TemplateType}

TemplateType.txt[4] = "SSI"


class TemplatePublishingMode(Enum):
    # Never publish this template
    DO_NOT_PUBLISH = 0
    # Only allow this template to be published from the template editor.
    MANUAL = 1
    # Queue this template for publication as soon as a post that depends on it
    # is also queued.
    QUEUE = 2


TemplatePublishingMode.txt = {
    x: x.name.replace("_", " ").lower().capitalize() for x in TemplatePublishingMode
}


class QueueObjType(Enum):
    CONTROL = 0
    WRITE_FILEINFO = 1
    DEL_FILEINFO = 2
    DEL_FILE = 3
    QUEUE_POST = 4


QueueObjType.txt = {
    QueueObjType.CONTROL: "Control",
    QueueObjType.WRITE_FILEINFO: "Write",
    QueueObjType.DEL_FILEINFO: "Delete",
    QueueObjType.DEL_FILE: "Del File",
    QueueObjType.QUEUE_POST: "Queue",
}


class QueueStatus(Enum):
    WAITING = 0
    RUNNING = 1
    FAILED = 2
    STOPPED = 3
    MANUAL = 4


QueueStatus.txt = {
    QueueStatus.WAITING: "Wait",
    QueueStatus.RUNNING: "Run",
    QueueStatus.FAILED: "Fail",
    QueueStatus.STOPPED: "Stop",
    QueueStatus.MANUAL: "Manual",
}
