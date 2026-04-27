"""First-iteration local file storage for form attachments.

Stores files under <LOCAL_STORAGE_ROOT>/<folder>/. Two folders are used:
- 'models'      → templates uploaded by admins (the PDF the alumno downloads).
- 'submissions' → files uploaded by alumnos as their answer to a Documento form.

The root directory is configured via the `LOCAL_STORAGE_ROOT` environment variable.
If unset, it defaults to `<BASE_DIR>/../data`, i.e. `ludo3/data` next to the backend.

This is intentionally a stand-in for cloud storage (Firebase/S3) so the feature
works end-to-end without any external service. Switch implementations by changing
the call sites; the public API is `upload`, `absolute_url`, `open_path`, `delete`.
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from django.conf import settings


_ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx'}


class LocalStorageService:
    MODELS = 'models'
    SUBMISSIONS = 'submissions'

    @classmethod
    def root(cls) -> Path:
        configured = os.environ.get('LOCAL_STORAGE_ROOT', '').strip()
        if configured:
            return Path(configured).expanduser().resolve()
        return (Path(settings.BASE_DIR).parent / 'data').resolve()

    @classmethod
    def folder_path(cls, folder: str) -> Path:
        if folder not in (cls.MODELS, cls.SUBMISSIONS):
            raise ValueError(f"Invalid folder '{folder}'. Use MODELS or SUBMISSIONS.")
        path = cls.root() / folder
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def upload(cls, file_obj, folder: str) -> str:
        ext = os.path.splitext(getattr(file_obj, 'name', ''))[1].lower()
        safe_ext = ext if ext in _ALLOWED_EXTENSIONS else ''
        filename = f"{uuid.uuid4().hex}{safe_ext}"
        dest = cls.folder_path(folder) / filename
        with open(dest, 'wb') as out:
            for chunk in file_obj.chunks():
                out.write(chunk)
        return filename

    @classmethod
    def absolute_url(cls, request, folder: str, filename: str) -> str:
        return request.build_absolute_uri(f'/api/files/{folder}/{filename}/')

    @classmethod
    def open_path(cls, folder: str, filename: str):
        path = cls.folder_path(folder) / filename
        return path if path.is_file() else None

    @classmethod
    def delete(cls, folder: str, filename: str) -> None:
        path = cls.folder_path(folder) / filename
        if path.is_file():
            path.unlink()

    @classmethod
    def filename_from_url(cls, url: str) -> Optional[str]:
        """Reverse of `absolute_url` — extracts the filename if the URL points
        to one of our local file endpoints; returns None otherwise (e.g. CMS URLs)."""
        if not url:
            return None
        for folder in (cls.MODELS, cls.SUBMISSIONS):
            marker = f'/api/files/{folder}/'
            if marker in url:
                tail = url.split(marker, 1)[1]
                return tail.rstrip('/').split('/', 1)[0]
        return None
