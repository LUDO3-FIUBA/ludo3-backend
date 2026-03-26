from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.http import FileResponse
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.model_validators.EvaluationSubmissionValidator import \
    EvaluationSubmissionValidator
from backend.models import Evaluation, EvaluationSubmission, Semester, Student
from backend.models.teacher import Teacher
from backend.models.teacher_role import TeacherRole
from backend.permissions import *
from backend.serializers.evaluation_submission_serializer import (
    EvaluationSubmissionCorrectionSerializer,
    EvaluationSubmissionPutSerializer, EvaluationSubmissionSerializer)
from backend.services.audit_log_service import AuditLogService
from backend.services.evaluation_submission_service import \
    EvaluationSubmissionService
from backend.services.grader_assignment_service import GraderAssignmentService
from backend.views.base_view import BaseViewSet
from backend.views.utils import (get_current_datetime,
                                 get_stub_chief_teacher_role,
                                 teacher_not_in_commission_staff)


class EvaluationSubmissionTeacherViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = EvaluationSubmission.objects.all()
    serializer_class = EvaluationSubmissionPutSerializer
        
    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Gets submissions for an evaluation",
        manual_parameters=[
            openapi.Parameter('evaluation', openapi.IN_QUERY, description="Id of evaluation to get submissions from", type=openapi.FORMAT_INT64)
        ]
    )
    def get_submissions(self, request):

        evaluation = get_object_or_404(Evaluation.objects, id=request.query_params["evaluation"])

        commission = evaluation.semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        result = self.queryset.filter(evaluation=request.query_params['evaluation']).all()
        return Response(EvaluationSubmissionCorrectionSerializer(result, many=True).data, status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Grades an evaluation submission"
    )
    def grade(self, request):
        grade = request.data.get('grade')
        submission_status = request.data.get('submission_status')
        submission = self.queryset.filter(student__user__id=request.data['student'], evaluation__id=request.data['evaluation']).first()

        if not submission:
            return Response("Submission not found", status=status.HTTP_404_NOT_FOUND)
        
        commission = submission.evaluation.semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        submissions_service = EvaluationSubmissionService()
        try:
            if submission_status is not None:
                submissions_service.set_status(submission, request.user.teacher, submission_status)
            else:
                submissions_service.set_grade(submission, request.user.teacher, grade)
        except ValidationError as e:
            payload = getattr(e, "message_dict", None) or {"detail": e.messages}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        AuditLogService().log(request.user, submission.student.user, f"Docente corrigio una entrega: {submission}")

        return Response(EvaluationSubmissionSerializer(submission).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Assigns a grader to an evaluation submission"
    )
    def assign_grader(self, request):
        grader_teacher = get_object_or_404(Teacher.objects, user_id=request.data['grader_teacher'])

        submission = self.queryset.filter(student__user__id=request.data['student'], evaluation__id=request.data['evaluation']).first()

        if not submission:
            return Response("Submission not found", status=status.HTTP_404_NOT_FOUND)
        
        if submission.grade:
            return Response("Submission already graded", status=status.HTTP_403_FORBIDDEN)

        commission = submission.evaluation.semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        if teacher_not_in_commission_staff(grader_teacher, commission):
            return Response("Teacher not present in commission's staff", status=status.HTTP_403_FORBIDDEN)

        submissions_service = EvaluationSubmissionService()
        submissions_service.set_grader(submission, grader_teacher)

        return Response(EvaluationSubmissionSerializer(submission).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['PUT'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Automatically assigns grader teachers to an evaluation"
    )
    def auto_assign_graders(self, request):
        evaluation: Evaluation = get_object_or_404(Evaluation.objects, id=request.data['evaluation'])

        if teacher_not_in_commission_staff(request.user.teacher, evaluation.semester.commission):
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        submissions = list(evaluation.submissions.all())
        teacher_roles = list(evaluation.semester.commission.teacher_roles.all())
        teacher_roles.append(get_stub_chief_teacher_role(evaluation.semester.commission))

        grader_assignment_service = GraderAssignmentService()
        new_submissions = grader_assignment_service.auto_assign(teacher_roles, submissions)

        return Response(EvaluationSubmissionSerializer(new_submissions, many=True).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Gets submissions for an evaluation",
        manual_parameters=[
            openapi.Parameter('student', openapi.IN_QUERY, description="Id of student to get submissions from", type=openapi.FORMAT_INT64),
            openapi.Parameter('semester', openapi.IN_QUERY, description="Id of semester to get submissions from", type=openapi.FORMAT_INT64)
        ]
    )
    def get_submissions_from_student(self, request):

        semester = get_object_or_404(Semester.objects, id=request.query_params["semester"])

        commission = semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        result = self.queryset.filter(evaluation__semester=semester).filter(student__user__id=request.query_params["student"]).all()
        return Response(EvaluationSubmissionCorrectionSerializer(result, many=True).data, status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'])
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Adds an evaluation submission for a student"
    )
    def add_evaluation_submission(self, request):
        grade = request.data['grade']

        evaluation = get_object_or_404(Evaluation.objects, id=request.data["evaluation"])

        student = get_object_or_404(Student.objects, user__id=request.data["student"])

        if(student not in evaluation.semester.students.all()):
            return Response("Student not in commission", status=status.HTTP_403_FORBIDDEN)

        submission = self.queryset.filter(student__user__id=request.data['student'], evaluation__id=request.data['evaluation']).first()

        if submission:
            return Response("Submission already exists", status=status.HTTP_403_FORBIDDEN)
        
        commission = evaluation.semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        
        submission = EvaluationSubmission(
            student=student,
            evaluation=evaluation,
            file=request.FILES.get("file"),
            submission_url=request.data.get("submission_url"),
            submission_text=request.data.get("submission_text"),
        )
        EvaluationSubmissionValidator(submission).validate()
        submission.full_clean()
        submission.save()

        AuditLogService().log(request.user, student.user, f"Docente agrego una entrega manualmente para la evaluacion: {evaluation}")

        if grade:
            submissions_service = EvaluationSubmissionService()
            submissions_service.set_grade(submission, request.user.teacher, grade)

            AuditLogService().log(request.user, submission.student.user, f"Docente corrigio una entrega {submission}")

        return Response(EvaluationSubmissionSerializer(submission).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='download-file')
    @swagger_auto_schema(
        tags=["Evaluation Submissions"],
        operation_summary="Downloads a submission file if teacher belongs to the commission"
    )
    def download_file(self, request, pk=None):
        submission = get_object_or_404(self.queryset, pk=pk)

        commission = submission.evaluation.semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        if not submission.file:
            return Response("Submission has no file", status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            submission.file.open('rb'),
            as_attachment=True,
            filename=submission.file.name.split('/')[-1]
        )