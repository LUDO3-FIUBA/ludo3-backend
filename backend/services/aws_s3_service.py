import os
import io
import pathlib
from typing import Optional

import boto3
from botocore.config import Config

from backend.utils import decode_image


class AwsS3Service:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            config=Config(signature_version='s3v4'),
        )
        self.bucket = os.environ["AWS_BUCKET_NAME"]
        domain = os.getenv("AWS_DOMAIN_URL") or os.getenv("AWS_PUBLIC_READ_DOMAIN")
        if domain:
            stripped = domain.rstrip('/')
            for prefix in ('https://', 'http://'):
                if stripped.startswith(prefix):
                    stripped = stripped[len(prefix):]
                    break
            self.public_read_domain = stripped
        else:
            self.public_read_domain = f"{self.bucket}.s3.amazonaws.com"

    def upload_b64_image(self, b64_string, file_name):
        return self.upload_object(io.BytesIO(decode_image(b64_string)), file_name)

    def upload_object(self, generic_object, file_name):
        file_content = generic_object.read()
        self.client.put_object(
            Bucket=self.bucket,
            Key=file_name,
            Body=file_content,
            ContentLength=len(file_content),
        )
        return f"https://{self.public_read_domain}/{file_name}"

    def download_object(self, file_name):
        return self.client.get_object(Bucket=self.bucket, Key=file_name)['Body']

    def delete_object(self, file_name: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=file_name)

    def generate_presigned_url(self, file_name: str, expiration: int = 3600) -> str:
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': file_name},
            ExpiresIn=expiration,
        )

    def key_from_url(self, url: str) -> Optional[str]:
        """Extracts the S3 object key from a public bucket URL."""
        if not url:
            return None
        prefix = f"https://{self.public_read_domain}/"
        if url.startswith(prefix):
            return url[len(prefix):]
        return None

    def presign_url(self, url: str, expiration: int = 3600) -> Optional[str]:
        """Returns a presigned URL for the given public bucket URL.

        For URLs outside the configured S3 bucket (e.g. external public links
        stored as a form's document_source), the URL is returned unchanged."""
        if not url:
            return None
        key = self.key_from_url(url)
        if not key:
            return url
        return self.generate_presigned_url(key, expiration)


class LocalStorageService:
    """File storage backed by the local filesystem. Used when USE_LOCAL_STORAGE=true."""

    def _media_root(self) -> pathlib.Path:
        from django.conf import settings
        return pathlib.Path(settings.MEDIA_ROOT)

    def _base_url(self) -> str:
        from django.conf import settings
        return settings.BASE_URL.rstrip('/') + settings.MEDIA_URL

    def upload_object(self, file_obj, file_name: str) -> str:
        dest = self._media_root() / file_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(file_obj.read())
        return self._base_url() + file_name

    def delete_object(self, file_name: str) -> None:
        p = self._media_root() / file_name
        if p.exists():
            p.unlink()

    def key_from_url(self, url: str) -> Optional[str]:
        prefix = self._base_url()
        if url and url.startswith(prefix):
            return url[len(prefix):]
        return None

    def presign_url(self, url: str, **_kwargs) -> Optional[str]:
        """Local files are already accessible; return the URL unchanged."""
        return url if url else None


def get_file_upload_service():
    """Return LocalStorageService when USE_LOCAL_STORAGE=true, otherwise AwsS3Service."""
    if os.environ.get('USE_LOCAL_STORAGE', '').lower() == 'true':
        return LocalStorageService()
    return AwsS3Service()
