from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Exists, OuterRef, Subquery
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Attendance, AttendanceQRCode, Semester
from backend.permissions import *
from backend.serializers.attendance_serializer import (
    AttendancePostSerializer,
    AttendanceQRCodeStudentStatusSerializer, AttendanceSerializer)
from backend.services.location_service import is_within_campus
from backend.views.base_view import BaseViewSet
from backend.views.utils import get_required_int_query_param, is_before_current_datetime


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

        if not semester.students.filter(pk=request.user.student.pk).exists():
            return Response("Student not in commission", status=status.HTTP_403_FORBIDDEN)

        if is_before_current_datetime(attendance_qr_code.expires_at):
            return Response("QR code has expired", status=status.HTTP_403_FORBIDDEN)

        if self.get_queryset().filter(student=request.user.student, qr_code=attendance_qr_code, semester=semester).first():
            return Response("This QR code has already been scanned", status=status.HTTP_403_FORBIDDEN)

        latitude = longitude = location_valid = None

        if attendance_qr_code.mode == 'qr_location':
            serializer = AttendancePostSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            latitude = serializer.validated_data.get('latitude')
            longitude = serializer.validated_data.get('longitude')
            if latitude is None or longitude is None:
                return Response(
                    {"detail": "latitude and longitude are required for qr_location sessions."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            location_valid = is_within_campus(attendance_qr_code.campus, latitude, longitude)

        attendance = Attendance(
            student=request.user.student,
            semester=semester,
            qr_code=attendance_qr_code,
            latitude=latitude,
            longitude=longitude,
            location_valid=location_valid,
        )
        attendance.save()
        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Attendances"],
        operation_summary="Gets attendance status timeline for semester",
        manual_parameters=[
            openapi.Parameter('semester_id', openapi.IN_QUERY, description="Id of semester", type=openapi.FORMAT_INT64)
        ]
    )
    def my_attendances(self, request):
        semester_id, error_response = get_required_int_query_param(request, 'semester_id')
        if error_response is not None:
            return error_response

        semester = get_object_or_404(Semester.objects, id=semester_id)

        if not semester.students.filter(pk=request.user.student.pk).exists():
            return Response("Student not in commission", status=status.HTTP_403_FORBIDDEN)

        student_attendances = Attendance.objects.filter(
            semester=semester,
            student=request.user.student,
            qr_code=OuterRef('pk'),
        )

        attendance_qr_codes = AttendanceQRCode.objects.filter(
            semester=semester,
        ).annotate(
            attended=Exists(student_attendances),
            submitted_at=Subquery(student_attendances.order_by('-submitted_at').values('submitted_at')[:1]),
            location_valid=Subquery(student_attendances.order_by('-submitted_at').values('location_valid')[:1]),
        ).order_by('-created_at')

        return Response(AttendanceQRCodeStudentStatusSerializer(attendance_qr_codes, many=True).data, status.HTTP_200_OK)
