from typing import Optional

from .client import NotionFlowClient


class Report:
    def __init__(self, auth: Optional[str] = None, parent_page_id: Optional[str] = None) -> None:
        self._client = NotionFlowClient(auth=auth, parent_page_id=parent_page_id)

    def generate_page_report(self, page_id: str) -> str:
        page_info = self._client.get_page(page_id=page_id)

    def generate_database_report(self, database_id: str) -> str:
        database_info = self._client.get_database(database_id=database_id)
