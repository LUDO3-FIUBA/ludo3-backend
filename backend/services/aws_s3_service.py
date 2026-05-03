import io
import os
from typing import Optional

import boto3

from backend.utils import decode_image


class AwsS3Service:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
        )
        self.bucket = os.environ["AWS_BUCKET_NAME"]
        domain = os.getenv("AWS_DOMAIN_URL") or os.getenv("AWS_PUBLIC_READ_DOMAIN")
        if domain:
            self.public_read_domain = domain.rstrip('/').removeprefix('https://').removeprefix('http://')
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
