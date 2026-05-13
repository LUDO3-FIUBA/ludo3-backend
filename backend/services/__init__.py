from .storage import get_storage_service


class _StorageServiceProxy:
	"""Lazily delegates calls to the provider selected in STORAGE_PROVIDER."""

	def __getattr__(self, name):
		return getattr(get_storage_service(), name)


storage_service = _StorageServiceProxy()

__all__ = ['get_storage_service', 'storage_service']
