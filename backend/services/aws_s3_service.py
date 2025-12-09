import os
import io

import boto3

from backend.utils import decode_image


class AwsS3Service:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            endpoint_url=os.getenv("AWS_ENDPOINT_URL")
        )
        self.bucket = os.environ["AWS_BUCKET_NAME"]
        self.public_read_domain = os.getenv("AWS_PUBLIC_READ_DOMAIN", f"{self.bucket}.s3.amazonaws.com")

    def upload_b64_image(self, b64_string, file_name):
        return self.upload_object(io.BytesIO(decode_image(b64_string)), file_name)

    def upload_object(self, generic_object, file_name):
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
        return f"https://{self.public_read_domain}/{file_name}"

    def download_object(self, file_name):
        return self.client.get_object(Bucket=self.bucket, Key=file_name)['Body']
