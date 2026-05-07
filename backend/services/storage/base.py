from abc import ABC, abstractmethod
import io


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
