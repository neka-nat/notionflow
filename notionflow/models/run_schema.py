import enum


class FieldTypes(enum.Enum):
    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    PEOPLE = "people"
    FILES = "files"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    FORMULA = "formula"
    RELATION = "relation"
    ROLLUP = "rollup"
    STATUS = "status"
    CREATED_TIME = "created_time"
    CREATED_BY = "created_by"
    LAST_EDITED_TIME = "last_edited_time"
    LAST_EDITED_BY = "last_edited_by"


class PageStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"

    @classmethod
    def values(cls) -> list[dict]:
        return [
            {
                "name": cls.SUCCESS.value,
                "color": "green",
            },
            {
                "name": cls.FAILED.value,
                "color": "red",
            },
            {
                "name": cls.RUNNING.value,
                "color": "yellow",
            },
        ]

    @classmethod
    def from_value(cls, value: str) -> "PageStatus":
        if value == cls.SUCCESS.value:
            return cls.SUCCESS
        elif value == cls.FAILED.value:
            return cls.FAILED
        elif value == cls.RUNNING.value:
            return cls.RUNNING
        else:
            raise ValueError(f"Invalid value: {value}")


def get_base_run_schema() -> dict:
    return {
        "name": {FieldTypes.TITLE.value: {}},
        "description": {FieldTypes.RICH_TEXT.value: {}},
        "date": {FieldTypes.DATE.value: {}},
        "user": {FieldTypes.PEOPLE.value: {}},
        "source": {FieldTypes.RICH_TEXT.value: {}},
        "version": {FieldTypes.RICH_TEXT.value: {}},
        "tags": {FieldTypes.MULTI_SELECT.value: {"options": []}},
        "artifacts": {FieldTypes.FILES.value: {}},
        "status": {FieldTypes.SELECT.value: {"options": PageStatus.values()}},
    }
