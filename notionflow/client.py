import os
import time
from dataclasses import dataclass
from typing import Optional, Union

from notion_client import Client

from notionflow.models import (
    DatabaseInfo,
    FieldTypes,
    PageInfo,
    PageStatus,
    get_base_run_schema,
)


@dataclass
class ResponseDB:
    res: bool
    id: Optional[str] = None


class NotionFlowClient:
    """NotionFlow client."""

    params_map = {
        "number": FieldTypes.NUMBER.value,
        "string": FieldTypes.RICH_TEXT.value,
        "category": FieldTypes.SELECT.value,
        "boolean": FieldTypes.CHECKBOX.value,
    }

    metrics_map = {
        "number": FieldTypes.NUMBER.value,
        "array": FieldTypes.RICH_TEXT.value,
    }

    def __init__(self, auth: Optional[str] = None, parent_page_id: Optional[str] = None) -> None:
        if auth is None:
            auth = os.environ.get("NOTION_TOKEN")
        if parent_page_id is None:
            parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID")

        self._notion_client = Client(auth=auth)
        self._parent_page_id = parent_page_id

    def create_database(
        self,
        database_title: str,
        params: Optional[dict] = None,
        metrics: Optional[dict] = None,
    ) -> ResponseDB:
        run_schema = get_base_run_schema()
        if params is not None:
            run_schema.update({f"Params[{key}]": {self.params_map[value]: {}} for key, value in params.items()})
        if metrics is not None:
            run_schema.update({f"Metrics[{key}]": {self.metrics_map[value]: {}} for key, value in metrics.items()})
        response = self._notion_client.databases.create(
            parent={"page_id": self._parent_page_id},
            title=[{"type": "text", "text": {"content": database_title}}],
            properties=run_schema,
        )
        database_id = response["id"]
        return ResponseDB(self._wait_db_create(database_id), database_id)

    def _wait_db_create(self, database_id: str, max_retry: int = 10) -> bool:
        cnt = 0
        while cnt < max_retry:
            if self._notion_client.databases.retrieve(database_id).get("object") == "database":
                return True
            time.sleep(1)
            cnt += 1
        return False

    def get_database(self, database_id: str) -> Optional[DatabaseInfo]:
        res = self._notion_client.databases.retrieve(database_id)
        return DatabaseInfo(**res)

    def get_database_by_name(self, name: str) -> Optional[DatabaseInfo]:
        db_list = self.get_db_list()
        for db in db_list:
            if len(db.title) >= 1 and db.title[0]["text"]["content"] == name:
                return db
        return None

    def get_db_list(self) -> list[DatabaseInfo]:
        infos = self._notion_client.search(filter={"property": "object", "value": "database"}).get("results")
        return [DatabaseInfo(**info) for info in infos]

    def add_empty_page(self, database_id: str, title: Optional[str] = None) -> PageInfo:
        res = self._notion_client.pages.create(
            parent={"database_id": database_id},
            properties={"name": {"title": [{"type": "text", "text": {"content": title or "New page"}}]}},
        )
        return PageInfo(**res)

    def log_param(self, page_id: str, key: str, value: Union[str, float, bool]) -> PageInfo:
        page_info = PageInfo(**self._notion_client.pages.retrieve(page_id))
        actual_key = f"Params[{key}]"
        if actual_key not in page_info.properties:
            raise KeyError(f"Key {key} not found in page {page_id}")
        property_type = page_info.properties[actual_key]["type"]
        if property_type == "number":
            new_value = {"number": value}
        elif property_type == "rich_text":
            new_value = {"rich_text": [{"type": "text", "text": {"content": value}}]}
        elif property_type == "select":
            new_value = {"select": {"name": value}}
        elif property_type == "checkbox":
            new_value = {"checkbox": value}
        else:
            raise ValueError(f"Unknown type: {property_type}")

        return PageInfo(**self._notion_client.pages.update(page_id, properties={actual_key: new_value}))

    def log_metric(self, page_id: str, key: str, value: float, step: Optional[int] = None) -> PageInfo:
        page_info = PageInfo(**self._notion_client.pages.retrieve(page_id))
        metric_property = self._metric_property(page_info, key, value, step)
        return PageInfo(**self._notion_client.pages.update(page_info.id, properties=metric_property))

    def _metric_property(self, page_info: PageInfo, key: str, value: float, step: Optional[int] = None) -> dict:
        actual_key = f"Metrics[{key}]"
        if actual_key not in page_info.properties:
            raise KeyError(f"Key {key} not found in page {page_info.id}")
        property_type = page_info.properties[actual_key]["type"]
        if property_type == "number":
            new_value = {"number": value}
        if property_type == "rich_text":
            property = page_info.properties[actual_key]
            if len(property["rich_text"]) == 0:
                current_value = [(step, value)]
            else:
                current_value = property["rich_text"][0]["text"]["content"]
                current_value = eval(current_value).append((step, value))
            new_value = {"rich_text": [{"type": "text", "text": {"content": str(current_value)}}]}
        return {actual_key: new_value}

    def log_metrics(self, page_id: str, values: dict[str, float], step: Optional[int] = None) -> PageInfo:
        page_info = PageInfo(**self._notion_client.pages.retrieve(page_id))
        metric_properties = {}
        for key, value in values.items():
            metric_property = self._log_metric(page_info, key, value, step)
            metric_properties.update(metric_property)
        return PageInfo(**self._notion_client.pages.update(page_info.id, properties=metric_properties))

    def log_artifact(self, page_id: str, local_path: str) -> PageInfo:
        pass

    def set_tag(self, page_id: str, tag: str, color: Optional[str] = None) -> PageInfo:
        page_info = PageInfo(**self._notion_client.pages.retrieve(page_id))
        if "tags" not in page_info.properties:
            raise KeyError(f"Key tags not found in page {page_info.id}")
        value = page_info.properties["tags"]
        value["multi_select"].append({"name": tag, "color": color or "default"})
        return PageInfo(**self._notion_client.pages.update(page_info.id, properties={"tags": value}))

    def set_status(self, page_id: str, status: Union[str, PageStatus]) -> PageInfo:
        if isinstance(status, PageStatus):
            status = status.value
        new_value = {"select": {"name": status}}
        return PageInfo(**self._notion_client.pages.update(page_id, properties={"status": new_value}))
