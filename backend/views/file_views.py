"""Endpoints to serve files stored locally via LocalStorageService.

- /api/files/models/<filename>      → form templates (public, no auth required)
- /api/files/submissions/<filename> → student submissions (admin only)

Missing Cloud Storage Support — this entire module can be removed once S3 is used;
files will be served directly from the bucket via public URL or presigned URL.
"""

import mimetypes

from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from backend.permissions import IsAdmin
from backend.services.local_storage_service import LocalStorageService


def _serve(folder: str, filename: str):
    path = LocalStorageService.open_path(folder, filename)
    if path is None:
        return Response({'detail': 'Archivo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    content_type, _ = mimetypes.guess_type(str(path))
    return FileResponse(open(path, 'rb'), content_type=content_type or 'application/octet-stream')


@api_view(['GET'])
@permission_classes([AllowAny])
def serve_model_file(request, filename):
    """Public endpoint — form templates can be opened via Linking.openURL without auth header."""
    return _serve(LocalStorageService.MODELS, filename)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def serve_submission_file(request, filename):
    return _serve(LocalStorageService.SUBMISSIONS, filename)
