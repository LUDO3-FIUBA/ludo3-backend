from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Secretary
from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
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
        if self.action in ('create', 'destroy', 'ownership_groups'):
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

    @swagger_auto_schema(tags=["Secretaries"], operation_summary="Set ownership group memberships for a secretary")
    @action(detail=True, methods=['patch'], url_path='ownership-groups')
    def ownership_groups(self, request, pk=None, *args, **kwargs):
        """
        PATCH /api/secretaries/{id}/ownership-groups/
        Payload: {"groups": [{"group_id": 1, "is_editor": true}, ...]}
        Atomically replaces all ownership-group memberships for this secretary.
        """
        secretary = get_object_or_404(self.get_queryset(), pk=pk)
        groups_data = request.data.get('groups', [])

        if not isinstance(groups_data, list):
            return Response({'detail': 'El campo "groups" debe ser una lista.'}, status=status.HTTP_400_BAD_REQUEST)

        validated = []
        for item in groups_data:
            if 'group_id' not in item or 'is_editor' not in item:
                return Response(
                    {'detail': 'Cada elemento debe tener "group_id" y "is_editor".'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                gid = int(item['group_id'])
            except (ValueError, TypeError):
                return Response({'detail': '"group_id" debe ser un entero.'}, status=status.HTTP_400_BAD_REQUEST)
            validated.append({'group_id': gid, 'is_editor': bool(item['is_editor'])})

        requested_ids = {v['group_id'] for v in validated}
        existing_groups = FormOwnershipGroup.objects.filter(id__in=requested_ids)
        if existing_groups.count() != len(requested_ids):
            return Response({'detail': 'Uno o más grupos no existen.'}, status=status.HTTP_400_BAD_REQUEST)

        # Guard: removing this entity must not leave any group without an editor.
        current_memberships = FormOwnershipMember.objects.filter(
            entity_type=FormOwnershipMember.SECRETARY, entity_id=secretary.id
        )
        current_group_ids = set(current_memberships.values_list('group_id', flat=True))
        groups_to_remove = current_group_ids - requested_ids
        for gid in groups_to_remove:
            group = FormOwnershipGroup.objects.get(id=gid)
            editors = group.members.filter(is_editor=True)
            is_sole_editor = editors.filter(
                entity_type=FormOwnershipMember.SECRETARY, entity_id=secretary.id
            ).exists() and editors.count() == 1
            if is_sole_editor:
                return Response(
                    {'detail': f'No se puede quitar a la secretaría del grupo "{group.name}" porque es su única editora.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            FormOwnershipMember.objects.filter(
                entity_type=FormOwnershipMember.SECRETARY,
                entity_id=secretary.id,
                group_id__in=groups_to_remove,
            ).delete()
            for v in validated:
                FormOwnershipMember.objects.update_or_create(
                    group_id=v['group_id'],
                    entity_type=FormOwnershipMember.SECRETARY,
                    entity_id=secretary.id,
                    defaults={'is_editor': v['is_editor']},
                )

        secretary.refresh_from_db()
        return Response(SecretarySerializer(secretary).data, status=status.HTTP_200_OK)
