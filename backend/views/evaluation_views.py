from datetime import timedelta

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Evaluation
from backend.models.evaluation_submission import EvaluationSubmission
from backend.permissions import *
from backend.serializers.evaluation_serializer import (
    EvaluationSemesterSerializer,
    EvaluationSerializer,
)
from backend.serializers.evaluation_submission_serializer import (
    EvaluationSubmissionSerializer,
)
from backend.views.base_view import BaseViewSet
from backend.views.utils import get_current_datetime


class EvaluationViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsStudent]
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer

    @swagger_auto_schema(
        tags=["Evaluations"],
        operation_summary="Gets evaluations from a semester",
        manual_parameters=[
            openapi.Parameter(
                "semester_id",
                openapi.IN_QUERY,
                description="Id of semester to get evaluations from",
                type=openapi.FORMAT_INT64,
            )
        ],
    )
    def list(self, request):
        semester_id = request.query_params.get("semester_id")
        if not semester_id:
            return Response({"semester_id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        result = self.get_queryset().filter(
            semester=semester_id
        )
        return Response(
            EvaluationSemesterSerializer(result, many=True).data, status.HTTP_200_OK
        )

    @action(detail=False, methods=["GET"])
    @swagger_auto_schema(
        tags=["Evaluations"],
        operation_summary="Gets future evaluations from semesters in which the logged in student student in inscripted in",
    )
    def mis_examenes(self, request):
        result = (
            self.queryset.filter(
                semester__students=request.user.student,
                end_date__gt=get_current_datetime() - timedelta(days=7),
            )
            .order_by("end_date")
            .all()
        )
        return Response(
            EvaluationSemesterSerializer(result, many=True).data, status.HTTP_200_OK
        )

    @action(detail=True, methods=["GET"])
    @swagger_auto_schema(
        tags=["Evaluations"],
        operation_summary="Gets current student's submissions for a given evaluation",
    )
    def my_submissions(self, request, pk=None):
        result = EvaluationSubmission.objects.filter(
            evaluation=pk, student=request.user.student
        ).all()
        return Response(
            EvaluationSubmissionSerializer(result, many=True).data, status.HTTP_200_OK
        )
