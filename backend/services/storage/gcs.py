import io
from typing import Optional

from .base import StorageService


class GcsStorageService(StorageService):
    """Google Cloud Storage provider (stub - to be implemented)"""

    def __init__(self):
        raise NotImplementedError(
            "Google Cloud Storage support is not yet implemented. "
            "Use STORAGE_PROVIDER=s3 or STORAGE_PROVIDER=local"
        )

    def upload_b64_image(self, b64_string: str, file_name: str) -> str:
        raise NotImplementedError()

    def upload_object(self, generic_object: io.IOBase, file_name: str) -> str:
        raise NotImplementedError()

    def public_url(self, key: str) -> str:
        raise NotImplementedError()

    def download_object(self, file_name: str) -> io.IOBase:
        raise NotImplementedError()

    def delete_object(self, file_name: str) -> None:
        raise NotImplementedError()

    def key_from_url(self, url: str) -> Optional[str]:
        raise NotImplementedError()

    def presign_url(self, url: str, expiration: int = 3600) -> Optional[str]:
        raise NotImplementedError()

    def get_download_url(self, file_name: str, filename_hint: str, expiration: int = 60) -> str | None:
        raise NotImplementedError()
