import os
import io
from typing import Optional

import boto3
from botocore.config import Config

from backend.utils import decode_image
from .base import StorageService


def _env_or_none(name):
    value = os.environ.get(name)
    if value is None:
        return None

    value = value.strip()
    return value or None


class AwsS3StorageService(StorageService):
    """AWS S3 storage provider"""

    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=_env_or_none("AWS_REGION") or _env_or_none("AWS_DEFAULT_REGION"),
            endpoint_url=_env_or_none("AWS_ENDPOINT_URL"),
            config=Config(signature_version='s3v4'),
        )
        self.bucket = os.environ.get("AWS_BUCKET_NAME")
        self.public_read_domain = os.getenv(
            "AWS_PUBLIC_READ_DOMAIN",
            f"{self.bucket}.s3.amazonaws.com"
        )

    def upload_b64_image(self, b64_string: str, file_name: str) -> str:
        return self.upload_object(io.BytesIO(decode_image(b64_string)), file_name)

    def upload_object(self, generic_object: io.IOBase, file_name: str) -> str:
        # Read the entire content to determine the content length
        # Oracle Cloud's S3-compatible API requires Content-Length header
        file_content = generic_object.read()

        # Use put_object instead of upload_fileobj to explicitly set Content-Length
        self.client.put_object(
            Bucket=self.bucket,
            Key=file_name,
            Body=file_content,
            ContentLength=len(file_content)
        )
        return self.public_url(file_name)

    def public_url(self, key: str) -> str:
        return f"https://{self.public_read_domain}/{key}"

    def download_object(self, file_name: str) -> io.IOBase:
        return self.client.get_object(Bucket=self.bucket, Key=file_name)['Body']

    def delete_object(self, file_name: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=file_name)

    def key_from_url(self, url: str) -> Optional[str]:
        if not url:
            return None
        prefix = f"https://{self.public_read_domain}/"
        if url.startswith(prefix):
            return url[len(prefix):]
        return None

    def presign_url(self, url: str, expiration: int = 3600) -> Optional[str]:
        if not url:
            return None
        key = self.key_from_url(url)
        if not key:
            return url
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expiration,
        )

    def get_download_url(self, file_name: str, filename_hint: str, expiration: int = 60) -> str | None:
        if not file_name or not self.bucket:
            return None

        safe_filename = filename_hint.replace('"', '\\"')

        return self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': file_name,
                'ResponseContentDisposition': f'attachment; filename="{safe_filename}"',
            },
            ExpiresIn=expiration,
        )
