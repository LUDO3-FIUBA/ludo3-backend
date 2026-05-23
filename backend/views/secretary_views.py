from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Secretary
from backend.permissions import IsAdmin, IsSuperAdmin
from backend.serializers.secretary_serializer import (
    SecretarySerializer,
    SecretaryListSerializer,
    SecretaryWriteSerializer,
)
from backend.views.base_view import BaseViewSet


def _get_admin_secretary_id(user):
    """Returns the secretary_id this admin is scoped to, or None for super admins / non-admins."""
    if not user.is_authenticated or not user.is_staff:
        return None
    if user.is_superuser:
        return None
    staff = getattr(user, 'staff', None)
    if staff is None:
        return None
    return staff.secretary_id


class SecretaryViewSet(BaseViewSet):
    queryset = Secretary.objects.all()
    serializer_class = SecretarySerializer

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [IsAuthenticated(), IsSuperAdmin()]
        if self.action in ('update', 'partial_update'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def _ensure_can_edit(self, request, secretary):
        if request.user.is_superuser:
            return
        if _get_admin_secretary_id(request.user) == secretary.id:
            return
        raise PermissionDenied("Solo podés editar tu propia secretaría.")

    @swagger_auto_schema(tags=["Secretaries"], operation_summary="List all secretaries")
    def list(self, request, *args, **kwargs):
        secretaries = Secretary.objects.filter(parent_secretary__isnull=True).prefetch_related('subsecretaries')
        return Response(SecretarySerializer(secretaries, many=True).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Secretaries"], operation_summary="Get a secretary")
    def retrieve(self, request, pk=None, *args, **kwargs):
        secretary = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(SecretarySerializer(secretary).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Secretaries"], operation_summary="Create a secretary", request_body=SecretaryWriteSerializer)
    def create(self, request, *args, **kwargs):
        serializer = SecretaryWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        secretary = serializer.save()
        return Response(SecretarySerializer(secretary).data, status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["Secretaries"], operation_summary="Update a secretary", request_body=SecretaryWriteSerializer)
    def update(self, request, pk=None, *args, **kwargs):
        secretary = get_object_or_404(self.get_queryset(), pk=pk)
        self._ensure_can_edit(request, secretary)
        serializer = SecretaryWriteSerializer(secretary, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(SecretarySerializer(secretary).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Secretaries"], operation_summary="Partial update a secretary", request_body=SecretaryWriteSerializer)
    def partial_update(self, request, pk=None, *args, **kwargs):
        secretary = get_object_or_404(self.get_queryset(), pk=pk)
        self._ensure_can_edit(request, secretary)
        serializer = SecretaryWriteSerializer(secretary, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(SecretarySerializer(secretary).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Secretaries"], operation_summary="Delete a secretary")
    def destroy(self, request, pk=None, *args, **kwargs):
        secretary = get_object_or_404(self.get_queryset(), pk=pk)
        secretary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
