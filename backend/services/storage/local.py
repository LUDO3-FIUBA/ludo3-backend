import os
import io
from pathlib import Path
from typing import Optional

from backend.utils import decode_image
from .base import StorageService


class LocalStorageService(StorageService):
    """Local filesystem storage provider (for development)"""

    def __init__(self):
        self.media_root = os.environ.get("LOCAL_MEDIA_ROOT", "./media")
        self.media_url = os.environ.get("LOCAL_MEDIA_URL", "/media/")
        base_url = os.environ.get("BASE_URL", "http://localhost:8000").rstrip('/')
        self.public_url_prefix = base_url + self.media_url

        Path(self.media_root).mkdir(parents=True, exist_ok=True)

    def upload_b64_image(self, b64_string: str, file_name: str) -> str:
        return self.upload_object(io.BytesIO(decode_image(b64_string)), file_name)

    def upload_object(self, generic_object: io.IOBase, file_name: str) -> str:
        full_path = os.path.join(self.media_root, file_name)
        Path(full_path).parent.mkdir(parents=True, exist_ok=True)

        file_content = generic_object.read()
        with open(full_path, 'wb') as f:
            f.write(file_content)

        return self.public_url(file_name)

    def public_url(self, key: str) -> str:
        return f"{self.public_url_prefix}{key}"

    def download_object(self, file_name: str) -> io.IOBase:
        full_path = os.path.join(self.media_root, file_name)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {file_name}")

        with open(full_path, 'rb') as f:
            return io.BytesIO(f.read())

    def delete_object(self, file_name: str) -> None:
        Path(self.media_root, file_name).unlink(missing_ok=True)

    def key_from_url(self, url: str) -> Optional[str]:
        if not url:
            return None
        if url.startswith(self.public_url_prefix):
            return url[len(self.public_url_prefix):]
        return None

    def presign_url(self, url: str, expiration: int = 3600) -> Optional[str]:
        return url if url else None
