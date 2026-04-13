from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Commission
from backend.permissions import IsAdmin
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

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="List all commissions")
    def list(self, request, *args, **kwargs):
        commissions = self.get_queryset()
        return Response(CommissionSerializer(commissions, many=True).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Get a commission")
    def retrieve(self, request, pk=None, *args, **kwargs):
        commission = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(CommissionSerializer(commission).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Create a commission", request_body=CommissionWriteSerializer)
    def create(self, request, *args, **kwargs):
        serializer = CommissionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        commission = serializer.save()
        return Response(CommissionSerializer(commission).data, status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Update a commission", request_body=CommissionWriteSerializer)
    def update(self, request, pk=None, *args, **kwargs):
        commission = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = CommissionWriteSerializer(commission, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CommissionSerializer(commission).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Commissions Admin"], operation_summary="Delete a commission")
    def destroy(self, request, pk=None, *args, **kwargs):
        commission = get_object_or_404(self.get_queryset(), pk=pk)
        commission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
