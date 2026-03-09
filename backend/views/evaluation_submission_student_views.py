from drf_yasg.utils import swagger_auto_schema
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.model_validators.EvaluationSubmissionValidator import \
    EvaluationSubmissionValidator
from backend.models import Evaluation, EvaluationSubmission
from backend.permissions import *
from backend.serializers.evaluation_submission_serializer import (
    EvaluationSubmissionPostSerializer, EvaluationSubmissionSerializer)
from backend.services.audit_log_service import AuditLogService
from backend.views.base_view import BaseViewSet


class EvaluationSubmissionViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsStudent]
    queryset = EvaluationSubmission.objects.all()
    serializer_class = EvaluationSubmissionPostSerializer
        
    @action(detail=False, methods=['POST'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Submit an evaluation"
    )
    def submit_evaluation(self, request):
        
        evaluation = get_object_or_404(Evaluation.objects, id=request.data["evaluation"])

        if(request.user.student not in evaluation.semester.students.all()):
            return Response("Student not in commission", status=status.HTTP_403_FORBIDDEN)

        submission = EvaluationSubmission(
            student=request.user.student,
            evaluation=evaluation,
            file=request.FILES.get("file"),
            submission_url=request.data.get("submission_url"),
            submission_text=request.data.get("submission_text"),
        )

        EvaluationSubmissionValidator(submission).validate()
        submission.full_clean()
        submission.save()

        AuditLogService().log(request.user, None, f"Estudiante realizo una entrega en la evaluación: {evaluation}")

        return Response(EvaluationSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Gets the logged in student's evaluation submissions"
    )
    def my_evaluations(self, request):

        result = self.queryset.filter(student=request.user.student).all()
        return Response(EvaluationSubmissionSerializer(result, many=True).data, status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='download-file')
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Downloads the logged in student's submission file"
    )
    def download_file(self, request, pk=None):
        submission = get_object_or_404(self.queryset, pk=pk)

        if submission.student != request.user.student:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        if not submission.file:
            return Response("Submission has no file", status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            submission.file.open('rb'),
            as_attachment=True,
            filename=submission.file.name.split('/')[-1]
        )