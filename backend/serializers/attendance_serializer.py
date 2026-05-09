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
    location_valid = serializers.BooleanField(allow_null=True)

    class Meta:
        model = Attendance
        fields = ('semester', 'student', 'qrid', 'submitted_at', 'location_valid')


class AttendanceNoSemesterNoQridSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    submitted_at = serializers.DateTimeField()
    location_valid = serializers.BooleanField(allow_null=True)

    class Meta:
        model = Attendance
        fields = ('student', 'submitted_at', 'location_valid')


class AttendanceNoSemesterSerializer(serializers.ModelSerializer):
    qrid = serializers.UUIDField(source='qr_code.qrid')
    submitted_at = serializers.DateTimeField()

    class Meta:
        model = Attendance
        fields = ('qrid', 'submitted_at')


class AttendanceQRCodeStudentStatusSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    qrid = serializers.UUIDField()
    attended = serializers.BooleanField()
    submitted_at = serializers.DateTimeField(allow_null=True)
    location_valid = serializers.BooleanField(allow_null=True)
    mode = serializers.CharField()
    campus = serializers.CharField(allow_null=True)

    class Meta:
        model = AttendanceQRCode
        fields = ('created_at', 'expires_at', 'qrid', 'attended', 'submitted_at', 'location_valid', 'mode', 'campus')


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
    mode = serializers.CharField()
    campus = serializers.CharField(allow_null=True)

    class Meta:
        model = AttendanceQRCode
        fields = ('semester', 'owner_teacher', 'created_at', 'expires_at', 'qrid', 'mode', 'campus')

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
    mode = serializers.CharField()
    campus = serializers.CharField(allow_null=True)

    class Meta:
        model = AttendanceQRCode
        fields = ('created_at', 'expires_at', 'qrid', 'attendances', 'mode', 'campus')


class AttendanceQRCodePostSerializer(serializers.ModelSerializer):
    semester = serializers.IntegerField()
    mode = serializers.ChoiceField(choices=['qr', 'location'], default='qr')
    campus = serializers.ChoiceField(choices=['las_heras', 'paseo_colon'], required=False, allow_null=True)

    class Meta:
        model = AttendanceQRCode
        fields = ('semester', 'mode', 'campus')

    def validate(self, data):
        if data.get('mode') == 'location' and not data.get('campus'):
            raise serializers.ValidationError("campus is required when mode is 'location'")
        return data


class AttendanceLocationPostSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class AttendanceAddStudentPostSerializer(serializers.ModelSerializer):
    qrid = serializers.UUIDField()
    student = serializers.IntegerField()

    class Meta:
        model = Attendance
        fields = ('qrid', 'student')
