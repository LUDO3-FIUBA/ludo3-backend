from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.core.exceptions import ValidationError
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
from backend.services.file_validator_service import FileValidatorService
from backend.views.base_view import BaseViewSet
from backend.views.utils import get_required_int_query_param


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

        evaluation_id = request.data.get("evaluation")
        if not evaluation_id:
            return Response({"evaluation": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        evaluation = get_object_or_404(Evaluation.objects, id=evaluation_id)

        if(request.user.student not in evaluation.semester.students.all()):
            return Response("Student not in commission", status=status.HTTP_403_FORBIDDEN)

        uploaded_file = request.FILES.get("submission_file") if "submission_file" in request.FILES else None
        uploaded_file, original_filename = FileValidatorService.prepare_upload_with_unique_name(uploaded_file)

        submission = EvaluationSubmission(
            student=request.user.student,
            evaluation=evaluation,
            submission_text=request.data.get("submission_text"),
            submission_file=uploaded_file,
            original_filename=original_filename,
        )

        try:
            EvaluationSubmissionValidator(submission).validate()
            submission.full_clean()
            submission.save()
        except ValidationError as e:
            payload = getattr(e, "message_dict", None) or {"detail": e.messages}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        AuditLogService().log(request.user, None, f"Estudiante realizo una entrega en la evaluación: {evaluation}")

        return Response(EvaluationSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Gets the logged in student's evaluation submissions for a semester",
        manual_parameters=[
            openapi.Parameter('semester_id', openapi.IN_QUERY, description="Id of semester", type=openapi.TYPE_INTEGER, required=True)
        ]
    )
    def my_evaluations(self, request):
        semester_id, error_response = get_required_int_query_param(request, 'semester_id')
        if error_response is not None:
            return error_response

        result = self.queryset.filter(
            student=request.user.student,
            evaluation__semester_id=semester_id
        )
        
        return Response(EvaluationSubmissionSerializer(result, many=True).data, status.HTTP_200_OK)