from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Prefetch
from itertools import groupby
from operator import itemgetter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Attendance, AttendanceQRCode, EvaluationSubmission, Semester
from backend.permissions import IsStudent, IsTeacher
from backend.serializers.semester_serializer import SemesterCommissionSerializer, SemesterSerializer
from backend.services.rule_engine_service import RuleEngineService
from backend.views.base_view import BaseViewSet
from backend.views.utils import get_current_semester, get_current_year, get_required_int_query_param, teacher_not_in_commission_staff


class SemesterViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    
    @action(detail=False, methods=["GET"])
    @swagger_auto_schema(
        tags=["Semesters"],
        operation_summary="Get semesters for a subject",
        manual_parameters=[
            openapi.Parameter('subject_siu_id', openapi.IN_QUERY, description="Id of subject to get semester from", type=openapi.FORMAT_INT64)
        ]
    )
    def subject_semesters(self, request):
        result = self.get_queryset().filter(commission__subject_siu_id=request.query_params['subject_siu_id'])
        return Response(self.get_serializer(result, many=True).data, status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"])
    @swagger_auto_schema(
        tags=["Semesters"],
        operation_summary="Get present semester for a subject",
        manual_parameters=[
            openapi.Parameter('subject_siu_id', openapi.IN_QUERY, description="Id of subject to get semester from", type=openapi.FORMAT_INT64)
        ]
    )
    def present_subject_semesters(self, request):
        result = self.get_queryset().filter(commission__subject_siu_id=request.query_params['subject_siu_id'], 
                                            start_date__year__gte=get_current_year(), year_moment=get_current_semester())
        return Response(self.get_serializer(result, many=True).data, status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated, IsTeacher])
    @swagger_auto_schema(
        tags=["Semesters"],
        operation_summary="Get semesters for a commission",
        manual_parameters=[
            openapi.Parameter('commission_id', openapi.IN_QUERY, description="Id of commission to get semester from", type=openapi.FORMAT_INT64)
        ]
    )
    def commission_present_semester(self, request):
        commission_id, error_response = get_required_int_query_param(request, 'commission_id')
        if error_response is not None:
            return error_response

        current_year = get_current_year()
        current_semester = get_current_semester()

        result = self.get_queryset().filter(
            commission=commission_id,
            start_date__year__gte=current_year,
            year_moment=current_semester,
        ).first()

        if result is None and current_semester == "SS":
            result = self.get_queryset().filter(
                commission=commission_id,
                start_date__year__gte=current_year,
                year_moment="FS",
            ).first()
        
        if not result:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        semester = result

        try:
            teacher = request.user.teacher
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Authenticated user has no teacher profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if teacher_not_in_commission_staff(teacher, semester.commission):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        attendance_qrs_count = semester.attendance_qrs.count()
        
        attendances_by_student = dict(
            semester.attendances.exclude(location_valid=False).values('student_id').annotate(total=Count('id')).values_list('student_id', 'total')
        )
        
        submissions = EvaluationSubmission.objects.filter(
            evaluation__semester=semester
        ).values(
            'student_id', 'evaluation_id', 'grade', 'submission_status'
        ).order_by('student_id')

        submissions_by_student = {}
        for student_id, group in groupby(submissions, key=itemgetter('student_id')):
            submissions_by_student[student_id] = list(group)

        serializer = SemesterCommissionSerializer(
            semester,
            context={
                'attendance_qrs_count': attendance_qrs_count,
                'attendances_by_student': attendances_by_student,
                'submissions_by_student': submissions_by_student,
            },
        )

        return Response(serializer.data, status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated, IsStudent])
    @swagger_auto_schema(
        tags=["Semesters"],
        operation_summary="Return if the student is passing the semester",
        manual_parameters=[
            openapi.Parameter('semester_id', openapi.IN_QUERY, description="Id of semester", type=openapi.FORMAT_INT64)
        ]
    )
    def is_passing(self, request):
        semester_id, error_response = get_required_int_query_param(request, 'semester_id')
        if error_response is not None:
            return error_response
        
        semester = self.get_queryset().filter(id=semester_id).first()
        if semester is None:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        attendance_qrs = AttendanceQRCode.objects.filter(semester=semester).prefetch_related(
            Prefetch(
                'attendances',
                queryset=Attendance.objects.filter(
                    semester=semester,
                    student=request.user.student,
                ),
            )
        )
        evaluation_submissions = EvaluationSubmission.objects.filter(
            evaluation__semester=semester,
            student=request.user.student,
        ).select_related('evaluation', 'grader')
        
        rule_engine_service = RuleEngineService()
        passed = rule_engine_service.is_student_passed(attendance_qrs, evaluation_submissions, request.user.student, semester)
        failed = rule_engine_service.is_student_failed(attendance_qrs, evaluation_submissions, request.user.student, semester)
        
        response = {'passed': passed, 'failed': failed}

        return Response(response, status.HTTP_200_OK)

