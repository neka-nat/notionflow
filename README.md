# notionflow

**WIP**
Notionflow is a library for experiment management in machine learning on notion.

## Installation

```bash
pip install notionflow
```

## Quick start

```bash
export NOTION_TOKEN=<your notion token>
export NOTION_PARENT_PAGE_ID=<parent page id>
```

```py
import notionflow as nf

nf.create_database("database1", {"param1": "number"}, {"recall": "number"})

with nf.start_page(page_name="page1") as page:
    nf.log_param("param1", 1.0)
    nf.log_metric("recall", 0.5)

with nf.start_page(page_name="page2") as page:
    nf.log_param("param1", 2.0)
    nf.log_metric("recall", 0.1)
```