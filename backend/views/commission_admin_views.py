from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Commission
from backend.permissions import IsAdmin, get_admin_department_id
from backend.serializers.commission_serializer import (
    CommissionSerializer,
    CommissionWriteSerializer,
)
from backend.views.base_view import BaseViewSet


class CommissionAdminViewSet(BaseViewSet):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def _scoped_queryset(self, request):
        qs = self.get_queryset()
        if request.user.is_superuser:
            return qs
        dept_id = get_admin_department_id(request.user)
        if dept_id is None:
            return qs.none()
        return qs.filter(department_id=dept_id)

    def _ensure_can_write(self, request, target_department_id):
        if request.user.is_superuser:
            return
        admin_dept = get_admin_department_id(request.user)
        if admin_dept is None:
            raise PermissionDenied("Solo super admins o admins de departamento pueden hacer esto.")
        if target_department_id != admin_dept:
            raise PermissionDenied("Solo podés gestionar comisiones de tu departamento.")

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="List all commissions")
    def list(self, request, *args, **kwargs):
        commissions = self._scoped_queryset(request)
        return Response(CommissionSerializer(commissions, many=True).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Get a commission")
    def retrieve(self, request, pk=None, *args, **kwargs):
        commission = get_object_or_404(self._scoped_queryset(request), pk=pk)
        return Response(CommissionSerializer(commission).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Create a commission", request_body=CommissionWriteSerializer)
    def create(self, request, *args, **kwargs):
        serializer = CommissionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_dept = serializer.validated_data.get('department')
        if target_dept is None and not request.user.is_superuser:
            target_dept_id = get_admin_department_id(request.user)
            if target_dept_id is None:
                raise ValidationError({"department": "El departamento es obligatorio."})
            serializer.validated_data['department_id'] = target_dept_id
        else:
            target_dept_id = target_dept.id if target_dept else None
            self._ensure_can_write(request, target_dept_id)
        commission = serializer.save()
        return Response(CommissionSerializer(commission).data, status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Update a commission", request_body=CommissionWriteSerializer)
    def update(self, request, pk=None, *args, **kwargs):
        return self._update(request, pk, partial=False)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Partial update a commission", request_body=CommissionWriteSerializer)
    def partial_update(self, request, pk=None, *args, **kwargs):
        return self._update(request, pk, partial=True)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Delete a commission")
    def destroy(self, request, pk=None, *args, **kwargs):
        commission = get_object_or_404(self.get_queryset(), pk=pk)
        self._ensure_can_write(request, commission.department_id)
        commission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, pk, partial):
        commission = get_object_or_404(self.get_queryset(), pk=pk)
        self._ensure_can_write(request, commission.department_id)
        serializer = CommissionWriteSerializer(commission, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_dept = serializer.validated_data.get('department', commission.department)
        new_dept_id = new_dept.id if new_dept else None
        if new_dept_id != commission.department_id:
            self._ensure_can_write(request, new_dept_id)
        serializer.save()
        return Response(CommissionSerializer(commission).data, status.HTTP_200_OK)
