from typing import Optional, Union

from .client import NotionFlowClient
from .models import DatabaseInfo, PageInfo, PageStatus
from .page import Page


class ActivePage(Page):
    def __init__(self, page_info: PageInfo):
        super().__init__(page_info)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = PageStatus.SUCCESS if exc_type is None else PageStatus.FAILED
        end_page(status)
        return exc_type is None


_active_page_stack: list[ActivePage] = []
_active_database_id: Optional[str] = None


def create_database(
    database_title: str, params: Optional[dict] = None, metrics: Optional[dict] = None
) -> DatabaseInfo:
    global _active_database_id
    database_info = NotionFlowClient().create_database(database_title, params, metrics)
    _active_database_id = database_info.id
    return database_info


def set_database(database_name: Optional[str] = None, database_id: Optional[str] = None) -> Optional[DatabaseInfo]:
    if database_name is not None and database_id is not None:
        raise ValueError("Only one of database_name and database_id should be set.")

    client = NotionFlowClient()
    database_info = None
    if database_name is not None and database_id is None:
        database_info = client.get_database_by_name(database_name)
    elif database_id is not None:
        database_info = client.get_database(database_id)
    global _active_database_id
    _active_database_id = database_info.id
    return database_info


def start_page(database_id: Optional[str] = None, page_name: Optional[str] = None) -> ActivePage:
    global _active_page_stack
    client = NotionFlowClient()
    page_info = client.add_empty_page(database_id or _active_database_id, page_name)
    active_page = ActivePage(page_info)
    _active_page_stack.append(active_page)
    return active_page


def log_param(key: str, value: Union[str, float, bool]) -> PageInfo:
    global _active_page_stack
    return NotionFlowClient().log_param(_active_page_stack[-1].page_info.id, key, value)


def log_metric(key: str, value: float, step: Optional[int] = None) -> PageInfo:
    global _active_page_stack
    return NotionFlowClient().log_metric(_active_page_stack[-1].page_info.id, key, value, step)


def log_metrics(values: dict[str, float], step: Optional[int] = None) -> PageInfo:
    global _active_page_stack
    return NotionFlowClient().log_metrics(_active_page_stack[-1].page_info.id, values, step)


def set_tag(tag: str, color: Optional[str] = None) -> PageInfo:
    global _active_page_stack
    return NotionFlowClient().set_tag(_active_page_stack[-1].page_info.id, tag, color)


def end_page(status: Union[str, PageStatus] = PageStatus.SUCCESS) -> PageInfo:
    global _active_page_stack
    active_page = _active_page_stack.pop()
    return NotionFlowClient().set_status(active_page.page_info.id, status)
