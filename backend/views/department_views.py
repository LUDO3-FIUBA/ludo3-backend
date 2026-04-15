from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Department
from backend.permissions import IsAdmin
from backend.serializers.department_serializer import DepartmentSerializer, DepartmentWriteSerializer
from backend.views.base_view import BaseViewSet


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

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
        serializer = DepartmentWriteSerializer(department, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DepartmentSerializer(department).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Departments"], operation_summary="Partial update a department", request_body=DepartmentWriteSerializer)
    def partial_update(self, request, pk=None, *args, **kwargs):
        department = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = DepartmentWriteSerializer(department, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DepartmentSerializer(department).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Departments"], operation_summary="Delete a department")
    def destroy(self, request, pk=None, *args, **kwargs):
        department = get_object_or_404(self.get_queryset(), pk=pk)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
