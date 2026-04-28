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
    def upload(cls, file_obj, folder: str, subfolder: str = '', name_prefix: str = '') -> str:
        """Store `file_obj` and return its key (relative path under `folder/`).

        When `subfolder` is given, the file is placed at
        ``folder/subfolder/{name_prefix}{uuid}{ext}``.
        The returned key is ``subfolder/{name_prefix}{uuid}{ext}`` — it may
        therefore contain a slash, which is intentional and handled by the
        rest of the API (open_path, delete, absolute_url, filename_from_url).
        """
        ext = os.path.splitext(getattr(file_obj, 'name', ''))[1].lower()
        safe_ext = ext if ext in _ALLOWED_EXTENSIONS else ''
        base = f"{name_prefix}{uuid.uuid4().hex}{safe_ext}"
        if subfolder:
            dest_dir = cls.folder_path(folder) / subfolder
            dest_dir.mkdir(parents=True, exist_ok=True)
            key = f"{subfolder}/{base}"
        else:
            dest_dir = cls.folder_path(folder)
            key = base
        with open(dest_dir / base, 'wb') as out:
            for chunk in file_obj.chunks():
                out.write(chunk)
        return key

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
        """Reverse of `absolute_url` — extracts the key (relative path that may
        include a subfolder) if the URL points to one of our local file endpoints;
        returns None otherwise (e.g. CMS URLs)."""
        if not url:
            return None
        for folder in (cls.MODELS, cls.SUBMISSIONS):
            marker = f'/api/files/{folder}/'
            if marker in url:
                tail = url.split(marker, 1)[1]
                return tail.rstrip('/')
        return None
