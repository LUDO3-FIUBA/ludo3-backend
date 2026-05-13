from datetime import timedelta

from django.db.models import Avg, Max, Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import (Attendance, AttendanceQRCode,
                            CommissionInscription, EvaluationSubmission,
                            Semester)
from backend.permissions import *
from backend.views.base_view import BaseViewSet
from backend.views.utils import (get_current_datetime,
                                 teacher_not_in_commission_staff)


class StatisticsTeacherViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated, IsTeacher]

    @swagger_auto_schema(
        tags=["Statistics"],
        operation_summary="Gets teacher statistics for a semester",
        manual_parameters=[
            openapi.Parameter('semester_id', openapi.IN_QUERY, description="Id of semester to get statistics from", type=openapi.FORMAT_INT64)
        ]
    )
    def list(self, request):

        semester = get_object_or_404(Semester.objects.get_queryset(), id=request.query_params["semester_id"])

        if(teacher_not_in_commission_staff(request.user.teacher, semester.commission)):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        results = {}

        # Semester Averages

        student_averages = EvaluationSubmission.objects.filter(
            evaluation__semester__commission=semester.commission).filter(
                evaluation__is_graded=True).filter(
                    grade__isnull=False).values(
                        'evaluation__semester__start_date__year', 
                        'evaluation__semester__year_moment', 
                        'student').annotate(student_average=Avg('grade')).all()

        results['semester_average'] = self._semester_averages(student_averages)

        # Retention Rate

        students_last_attended_class = Attendance.objects.get_queryset().filter(semester=semester).exclude(location_valid=False).values(
            'student').annotate(last_attendance=Max('qr_code__created_at'))
        
        classes_with_attendance = AttendanceQRCode.objects.get_queryset().filter(semester=semester).order_by('created_at').all()

        desertions = []
        desertion_amount = 0

        for class_with_attendance in classes_with_attendance:
            desertion_in_class = {'date': class_with_attendance.created_at}
            for student in students_last_attended_class:
                if desertion_in_class['date'] == student['last_attendance']:
                    desertion_amount += 1
            
            desertion_in_class['students_deserted'] = desertion_amount
            desertions.append(desertion_in_class)
            desertion_amount = 0

        desertions_without_last = desertions[:-1] # exclude last data point because it will always detect desertions
        results["desertions"] = desertions_without_last

        # Assistance Rate

        attendances_amount = Attendance.objects.get_queryset().filter(semester=semester).exclude(location_valid=False).count()
        classes_with_attendance_amount = len(classes_with_attendance)

        condition1 = Q(status='P')
        condition2 = Q(status='A')
        students_amount = CommissionInscription.objects.get_queryset().filter(semester=semester).filter(condition1 | condition2).count()

        ideal_total_attendances = classes_with_attendance_amount * students_amount
        if ideal_total_attendances > 0:
            results["attendance_rate"] = attendances_amount / ideal_total_attendances

        return Response(results, status=status.HTTP_200_OK)
    

    def _semester_averages(self, student_averages):
        semester_averages = {}

        for student_average in student_averages:
            key = str(student_average["evaluation__semester__start_date__year"]) + "-" + student_average["evaluation__semester__year_moment"]
            if key not in semester_averages:
                semester_averages[key] = {
                    "year": student_average["evaluation__semester__start_date__year"],
                    "year_moment": student_average["evaluation__semester__year_moment"],
                    "total_average": student_average["student_average"],
                    "count": 1
                }
            else:
                semester_averages[key]["total_average"] += student_average["student_average"]
                semester_averages[key]["count"] += 1

        semester_averages_list = []

        for key, value in semester_averages.items():
            semester_averages_list.append({
                "average": value["total_average"] / value["count"],
                "year": value["year"],
                "year_moment": value["year_moment"]
            })

        def sort_key(semester):
            return (semester["year"], semester["year_moment"])

        semester_averages_list.sort(key=sort_key)

        last_five_semesters = semester_averages_list[-5:]

        return last_five_semesters
