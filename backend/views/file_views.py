"""Endpoints to serve files stored locally via LocalStorageService.

- /api/files/models/<filename>      → form templates (any authenticated user)
- /api/files/submissions/<filename> → student submissions (admin only)
"""

import mimetypes

from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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
@permission_classes([IsAuthenticated])
def serve_model_file(request, filename):
    return _serve(LocalStorageService.MODELS, filename)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def serve_submission_file(request, filename):
    return _serve(LocalStorageService.SUBMISSIONS, filename)
