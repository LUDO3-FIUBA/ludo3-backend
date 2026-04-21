from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Attendance, AttendanceQRCode, Semester
from backend.permissions import *
from backend.serializers.attendance_serializer import (
    AttendanceNoSemesterSerializer, AttendancePostSerializer,
    AttendanceSerializer)
from backend.views.base_view import BaseViewSet
from backend.views.utils import is_before_current_datetime


class AttendanceViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsStudent]
    queryset = Attendance.objects.all()
    serializer_class = AttendancePostSerializer

    @swagger_auto_schema(
        tags=["Attendances"],
        operation_summary="Submit an attendance"
    )
    def create(self, request):
        attendance_qr_code = get_object_or_404(AttendanceQRCode.objects, qrid=request.data['qrid'])
        semester = attendance_qr_code.semester

        if request.user.student not in semester.students.all():
            return Response("Student not in commission", status=status.HTTP_403_FORBIDDEN)

        if is_before_current_datetime(attendance_qr_code.expires_at):
            return Response("QR code has expired", status=status.HTTP_403_FORBIDDEN)

        if self.get_queryset().filter(student=request.user.student, qr_code=attendance_qr_code, semester=semester).first():
            return Response("This QR code has already been scanned", status=status.HTTP_403_FORBIDDEN)

        attendance = Attendance(student=request.user.student, semester=semester, qr_code=attendance_qr_code)
        attendance.save()
        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Attendances"],
        operation_summary="Gets attendances for semester",
        manual_parameters=[
            openapi.Parameter('semester_id', openapi.IN_QUERY, description="Id of semester", type=openapi.FORMAT_INT64)
        ]
    )
    def my_attendances(self, request):
        semester = get_object_or_404(Semester.objects, id=request.query_params['semester_id'])

        if request.user.student not in semester.students.all():
            return Response("Student not in commission", status=status.HTTP_403_FORBIDDEN)

        attendances = Attendance.objects.filter(
            semester=semester,
            student=request.user.student,
        ).order_by('-submitted_at')

        return Response(AttendanceNoSemesterSerializer(attendances, many=True).data, status.HTTP_200_OK)
