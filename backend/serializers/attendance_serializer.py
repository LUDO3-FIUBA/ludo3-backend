from rest_framework import serializers

from backend.models import Attendance, AttendanceQRCode

from .semester_serializer import SemesterSerializer
from .student_serializer import StudentSerializer
from .teacher_serializer import TeacherSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer()
    student = StudentSerializer()
    qrid = serializers.UUIDField(source='qr_code.qrid')
    submitted_at = serializers.DateTimeField()

    class Meta:
        model = Attendance
        fields = ('semester', 'student', 'qrid', 'submitted_at')


class AttendanceNoSemesterNoQridSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    submitted_at = serializers.DateTimeField()

    class Meta:
        model = Attendance
        fields = ('student', 'submitted_at')


class AttendanceNoSemesterSerializer(serializers.ModelSerializer):
    qrid = serializers.UUIDField(source='qr_code.qrid')
    submitted_at = serializers.DateTimeField()

    class Meta:
        model = Attendance
        fields = ('qrid', 'submitted_at')


class AttendancePostSerializer(serializers.ModelSerializer):
    qrid = serializers.UUIDField()

    class Meta:
        model = Attendance
        fields = ('qrid',)


class AttendanceQRCodeSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer()
    owner_teacher = TeacherSerializer()
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    qrid = serializers.UUIDField()

    class Meta:
        model = AttendanceQRCode
        fields = ('semester', 'owner_teacher', 'created_at', 'expires_at', 'qrid')

class AttendanceQRCodeSerializerNoSemester(serializers.ModelSerializer):
    owner_teacher = TeacherSerializer()
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    qrid = serializers.UUIDField()

    class Meta:
        model = AttendanceQRCode
        fields = ('owner_teacher', 'created_at', 'expires_at', 'qrid')


class AttendanceQRCodeStudentsSerializerNoSemester(serializers.ModelSerializer):
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    qrid = serializers.UUIDField()
    attendances = AttendanceNoSemesterNoQridSerializer(many=True)

    class Meta:
        model = AttendanceQRCode
        fields = ('created_at', 'expires_at', 'qrid', 'attendances')


class AttendanceQRCodePostSerializer(serializers.ModelSerializer):
    semester = serializers.IntegerField()

    class Meta:
        model = AttendanceQRCode
        fields = ('semester',)


class AttendanceAddStudentPostSerializer(serializers.ModelSerializer):
    qrid = serializers.UUIDField()
    student = serializers.IntegerField()

    class Meta:
        model = Attendance
        fields = ('qrid', 'student')
