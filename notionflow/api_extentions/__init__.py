from notion_client import Client

from .upload import S3UploadEndpoint


def extend_notion_client(notion_client: Client) -> Client:
    notion_client.s3uploads = S3UploadEndpoint(notion_client)
    return notion_client
