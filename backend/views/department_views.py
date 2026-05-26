from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Department
from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from backend.permissions import IsAdmin, IsSuperAdmin, get_admin_department_id
from backend.serializers.department_serializer import DepartmentSerializer, DepartmentWriteSerializer
from backend.views.base_view import BaseViewSet


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ('create', 'destroy', 'ownership_groups'):
            return [IsAuthenticated(), IsSuperAdmin()]
        if self.action in ('update', 'partial_update'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def _ensure_can_edit(self, request, department):
        if request.user.is_superuser:
            return
        if get_admin_department_id(request.user) == department.id:
            return
        raise PermissionDenied("Solo podés editar tu propio departamento.")

    @swagger_auto_schema(tags=["Departments"], operation_summary="List all departments")
    def list(self, request, *args, **kwargs):
        departments = self.get_queryset()
        return Response(DepartmentSerializer(departments, many=True).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Departments"], operation_summary="Get a department")
    def retrieve(self, request, pk=None, *args, **kwargs):
        department = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(DepartmentSerializer(department).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Departments"], operation_summary="Create a department", request_body=DepartmentWriteSerializer)
    def create(self, request, *args, **kwargs):
        serializer = DepartmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = serializer.save()
        return Response(DepartmentSerializer(department).data, status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["Departments"], operation_summary="Update a department", request_body=DepartmentWriteSerializer)
    def update(self, request, pk=None, *args, **kwargs):
        department = get_object_or_404(self.get_queryset(), pk=pk)
        self._ensure_can_edit(request, department)
        serializer = DepartmentWriteSerializer(department, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DepartmentSerializer(department).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Departments"], operation_summary="Partial update a department", request_body=DepartmentWriteSerializer)
    def partial_update(self, request, pk=None, *args, **kwargs):
        department = get_object_or_404(self.get_queryset(), pk=pk)
        self._ensure_can_edit(request, department)
        serializer = DepartmentWriteSerializer(department, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DepartmentSerializer(department).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Departments"], operation_summary="Delete a department")
    def destroy(self, request, pk=None, *args, **kwargs):
        department = get_object_or_404(self.get_queryset(), pk=pk)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(tags=["Departments"], operation_summary="Set ownership group memberships for a department")
    @action(detail=True, methods=['patch'], url_path='ownership-groups')
    def ownership_groups(self, request, pk=None, *args, **kwargs):
        """
        PATCH /api/departments/{id}/ownership-groups/
        Payload: {"groups": [{"group_id": 1, "is_editor": true}, ...]}
        Atomically replaces all ownership-group memberships for this department.
        """
        department = get_object_or_404(self.get_queryset(), pk=pk)
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
            entity_type=FormOwnershipMember.DEPARTMENT, entity_id=department.id
        )
        current_group_ids = set(current_memberships.values_list('group_id', flat=True))
        groups_to_remove = current_group_ids - requested_ids
        for gid in groups_to_remove:
            group = FormOwnershipGroup.objects.get(id=gid)
            editors = group.members.filter(is_editor=True)
            is_sole_editor = editors.filter(
                entity_type=FormOwnershipMember.DEPARTMENT, entity_id=department.id
            ).exists() and editors.count() == 1
            if is_sole_editor:
                return Response(
                    {'detail': f'No se puede quitar al departamento del grupo "{group.name}" porque es su único editor.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            FormOwnershipMember.objects.filter(
                entity_type=FormOwnershipMember.DEPARTMENT,
                entity_id=department.id,
                group_id__in=groups_to_remove,
            ).delete()
            for v in validated:
                FormOwnershipMember.objects.update_or_create(
                    group_id=v['group_id'],
                    entity_type=FormOwnershipMember.DEPARTMENT,
                    entity_id=department.id,
                    defaults={'is_editor': v['is_editor']},
                )

        department.refresh_from_db()
        return Response(DepartmentSerializer(department).data, status=status.HTTP_200_OK)
