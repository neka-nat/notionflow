import boto3

from notion_client.api_endpoints import Endpoint


class S3UploadEndpoint(Endpoint):
    def upload_file(self, path: str, bucket: str, key: str) -> str:
        s3 = boto3.client("s3")
        s3.upload_file(path, bucket, key)
        return "%s/%s/%s" % (s3.meta.endpoint_url, bucket, key)
