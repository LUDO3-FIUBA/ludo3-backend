from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Commission, Semester
from backend.serializers.commission_serializer import CommissionSerializer
from backend.serializers.semester_serializer import SemesterSerializer
from backend.views.base_view import BaseViewSet


class CommissionViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer

    @swagger_auto_schema(
        tags=["Commissions"],
        operation_summary="Gets all commissions"
    )
    def list(self, request, *args, **kwargs):
        result = self.get_queryset()
        return Response(self.get_serializer(result, many=True).data, status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"])
    @swagger_auto_schema(
        tags=["Commissions"],
        operation_summary="Gets all commissions for a subject",
        manual_parameters=[
            openapi.Parameter('subject_siu_id', openapi.IN_QUERY, description="Id of subject to get commission from", type=openapi.FORMAT_INT64)
        ]
    )
    def subject_commissions(self, request):
        result = self.get_queryset().filter(subject_siu_id=request.query_params['subject_siu_id'])
        return Response(self.get_serializer(result, many=True).data, status.HTTP_200_OK)
    
    @action(detail=True, methods=["GET"])
    @swagger_auto_schema(
        tags=["Commissions"],
        operation_summary="Gets all commissions for a subject",
        manual_parameters=[
            openapi.Parameter('subject_siu_id', openapi.IN_QUERY, description="Id of subject to get commission from", type=openapi.FORMAT_INT64)
        ]
    )
    def semesters(self, request, pk=None):
        commission = get_object_or_404(self.queryset, id=pk)
        result = Semester.objects.get_queryset().filter(commission=commission)
        return Response(SemesterSerializer(result, many=True).data, status.HTTP_200_OK)

