from pydantic import BaseModel, Extra


class BlockInfo(BaseModel):
    """Notion block info.

    This class is a Pydantic model for the Notion block info object.
    See the Notion API reference for more information:
    https://developers.notion.com/reference/block
    """

    object: str
    id: str
    parent: dict
    type: str
    created_time: str
    created_by: dict
    last_edited_time: str
    last_edited_by: dict
    has_children: bool
    archived: bool

    class Config:
        extra = Extra.allow
