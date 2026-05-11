from abc import ABC, abstractmethod
import io
from typing import Optional


class StorageService(ABC):
    """Abstract base class for storage providers (S3, GCS, Local, etc.)"""

    @abstractmethod
    def upload_b64_image(self, b64_string: str, file_name: str) -> str:
        """
        Upload a base64-encoded image to storage.

        Args:
            b64_string: Base64-encoded image data
            file_name: Name to save the file as

        Returns:
            Public URL to access the uploaded file
        """
        pass

    @abstractmethod
    def upload_object(self, generic_object: io.IOBase, file_name: str) -> str:
        """
        Upload a file object to storage.

        Args:
            generic_object: File-like object (BytesIO, open file, etc.)
            file_name: Name to save the file as

        Returns:
            Public URL to access the uploaded file
        """
        pass

    @abstractmethod
    def download_object(self, file_name: str) -> io.IOBase:
        """
        Download a file from storage.

        Args:
            file_name: Name of the file to download

        Returns:
            File-like object with the content
        """
        pass

    @abstractmethod
    def delete_object(self, file_name: str) -> None:
        """
        Delete a file from storage.

        Args:
            file_name: Name of the file to delete
        """
        pass

    @abstractmethod
    def key_from_url(self, url: str) -> Optional[str]:
        """
        Extract the storage key from a URL produced by this provider.

        Args:
            url: URL previously returned by upload_object/upload_b64_image

        Returns:
            The storage key, or None if the URL does not belong to this provider.
        """
        pass

    @abstractmethod
    def presign_url(self, url: str, expiration: int = 3600) -> Optional[str]:
        """
        Return a temporary signed URL for a privately-stored object.

        For URLs that do not belong to this provider (e.g. external links), the
        URL is returned unchanged. Implementations that don't require signing
        (e.g. local filesystem) should return the URL unchanged.

        Args:
            url: URL previously returned by upload_object/upload_b64_image
            expiration: Signed URL lifetime in seconds (default: 3600)

        Returns:
            A URL the client can fetch, or None if `url` is empty.
        """
        pass
