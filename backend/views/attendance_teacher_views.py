from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Attendance, AttendanceQRCode, Semester
from backend.permissions import *
from backend.serializers.attendance_serializer import (
    AttendanceQRCodePostSerializer, AttendanceQRCodeSerializer,
    AttendanceQRCodeStudentsSerializerNoSemester)
from backend.views.base_view import BaseViewSet
from backend.views.utils import teacher_not_in_commission_staff


class AttendanceTeacherViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = Attendance.objects.all()
    serializer_class = AttendanceQRCodePostSerializer

    @action(detail=False, methods=['POST', 'DELETE'])
    @swagger_auto_schema(
        tags=["Attendance QRs"],
        operation_summary="Create or delete an attendance QR code"
    )
    def qr(self, request):
        if request.method == 'DELETE':
            attendance_qr = get_object_or_404(AttendanceQRCode.objects, qrid=request.data.get('qrid'))
            commission = attendance_qr.semester.commission
            if teacher_not_in_commission_staff(request.user.teacher, commission):
                return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)
            attendance_qr.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AttendanceQRCodePostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        semester = get_object_or_404(Semester.objects, id=serializer.validated_data['semester'])
        owner_teacher = request.user.teacher

        commission = semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        mode = serializer.validated_data.get('mode', 'qr')
        campus = serializer.validated_data.get('campus')
        attendance_qr = AttendanceQRCode(semester=semester, owner_teacher=owner_teacher, mode=mode, campus=campus)
        attendance_qr.save()
        return Response(AttendanceQRCodeSerializer(attendance_qr).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    @swagger_auto_schema(
        tags=["Attendance QRs"],
        operation_summary="Get latest valid QR code or create new one"
    )
    def latest_qr(self, request):
        serializer = AttendanceQRCodePostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        semester = get_object_or_404(Semester.objects, id=serializer.validated_data['semester'])
        owner_teacher = request.user.teacher

        commission = semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        mode = serializer.validated_data.get('mode', 'qr')
        campus = serializer.validated_data.get('campus')

        valid_qr = semester.attendance_qrs.filter(
            expires_at__gt=timezone.now(),
            mode=mode,
            campus=campus,
        ).order_by('-created_at').first()

        if valid_qr:
            return Response(AttendanceQRCodeSerializer(valid_qr).data, status=status.HTTP_200_OK)
        else:
            attendance_qr = AttendanceQRCode(semester=semester, owner_teacher=owner_teacher, mode=mode, campus=campus)
            attendance_qr.save()
            return Response(AttendanceQRCodeSerializer(attendance_qr).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=["Attendances"],
        operation_summary="Get attendances for a semester"
    )
    def list(self, request):
        semester = get_object_or_404(Semester.objects, id=request.query_params['semester_id'])

        commission = semester.commission
        if teacher_not_in_commission_staff(request.user.teacher, commission):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        attendances = AttendanceQRCode.objects.filter(semester=semester).all()

        return Response(AttendanceQRCodeStudentsSerializerNoSemester(attendances, many=True).data, status.HTTP_200_OK)
