import os
from typing import Optional

from .base import StorageService
from .aws import AwsS3StorageService
from .local import LocalStorageService
from .gcs import GcsStorageService


_storage_instance: Optional[StorageService] = None
_current_provider: Optional[str] = None


def get_storage_service() -> StorageService:
    """
    Factory function to get the configured storage service instance.
    
    Returns the appropriate storage provider based on STORAGE_PROVIDER env var.
    Implements singleton pattern (one instance per process).
    
    Environment variables:
        STORAGE_PROVIDER: 'local', 's3', or 'gcs' (default: 'local')
        
    For AWS S3:
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY
        - AWS_BUCKET_NAME
        - AWS_ENDPOINT_URL (optional)
        - AWS_PUBLIC_READ_DOMAIN (optional)
        
    For Local storage:
        - LOCAL_MEDIA_ROOT (optional, default: './media')
        - LOCAL_MEDIA_URL (optional, default: '/media/')
        
    For Google Cloud Storage:
        - GOOGLE_APPLICATION_CREDENTIALS (optional)
        - GCS_BUCKET_NAME
        
    Returns:
        StorageService instance
        
    Raises:
        ValueError: If STORAGE_PROVIDER is invalid
        NotImplementedError: If GCS is selected (not yet implemented)
    """
    global _storage_instance, _current_provider
    
    provider = os.environ.get('STORAGE_PROVIDER', 'local').lower()
    
    if _storage_instance is not None and _current_provider == provider:
        return _storage_instance
    
    if provider == 'local':
        _storage_instance = LocalStorageService()
    elif provider == 's3':
        _storage_instance = AwsS3StorageService()
    elif provider == 'gcs':
        _storage_instance = GcsStorageService()
    else:
        raise ValueError(
            f"Invalid STORAGE_PROVIDER: {provider}. "
            f"Must be one of: 'local', 's3', 'gcs'"
        )
    
    _current_provider = provider
    return _storage_instance
