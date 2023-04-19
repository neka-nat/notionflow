from typing import Optional

from pydantic import BaseModel


class PageInfo(BaseModel):
    """Notion page info.

    This class is a Pydantic model for the Notion page info object.
    See the Notion API reference for more information:
    https://developers.notion.com/reference/page
    """

    object: str
    id: str
    cover: Optional[str]
    icon: Optional[str]
    created_time: str
    created_by: dict
    last_edited_by: dict
    last_edited_time: str
    properties: dict
    parent: dict
    url: str
    archived: bool
