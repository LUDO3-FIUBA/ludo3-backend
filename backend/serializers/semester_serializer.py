from rest_framework import serializers

from backend.models import Semester, EvaluationSubmission

from .commission_serializer import CommissionSerializer
from .evaluation_serializer import (EvaluationSerializer,
                                    EvaluationWithMakeupSerializer)
from .student_serializer import StudentSerializer
from .semester_schedule_serializer import SemesterScheduleSerializer


class SemesterSubmissionSerializer(serializers.Serializer):
    evaluation_id = serializers.IntegerField()
    grade = serializers.IntegerField(allow_null=True)
    submission_status = serializers.CharField(allow_null=True)


class SemesterSerializer(serializers.ModelSerializer):
    year_moment = serializers.CharField()
    start_date = serializers.DateTimeField()
    commission = CommissionSerializer()
    evaluations = EvaluationSerializer(many=True)
    students = StudentSerializer(many=True)
    classes_amount = serializers.IntegerField()
    minimum_attendance = serializers.FloatField()
    schedules = SemesterScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Semester
        fields = ('id', 'year_moment', 'start_date', 'commission', 'evaluations', 'students', 'classes_amount', 'minimum_attendance', 'schedules')


class SemesterCommissionStudentSerializer(StudentSerializer):
    attendances_count = serializers.SerializerMethodField()
    submissions = serializers.SerializerMethodField()

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ('attendances_count', 'submissions')

    def get_attendances_count(self, obj):
        attendances_by_student = self.context.get('attendances_by_student', {})
        return attendances_by_student.get(obj.pk, 0)

    def get_submissions(self, obj):
        submissions_by_student = self.context.get('submissions_by_student', {})
        submissions_list = submissions_by_student.get(obj.pk, [])
        return SemesterSubmissionSerializer(submissions_list, many=True).data


class SemesterCommissionSerializer(serializers.ModelSerializer):
    year_moment = serializers.CharField()
    start_date = serializers.DateTimeField()
    commission = CommissionSerializer()
    evaluations = EvaluationSerializer(many=True)
    students = SemesterCommissionStudentSerializer(many=True)
    classes_amount = serializers.IntegerField()
    minimum_attendance = serializers.FloatField()
    schedules = SemesterScheduleSerializer(many=True, read_only=True)
    attendance_qrs_count = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = (
            'id',
            'year_moment',
            'start_date',
            'commission',
            'evaluations',
            'students',
            'classes_amount',
            'minimum_attendance',
            'schedules',
            'attendance_qrs_count',
        )

    def get_attendance_qrs_count(self, obj):
        return self.context.get('attendance_qrs_count', 0)


class SemesterWithMakeupSerializer(serializers.ModelSerializer):
    year_moment = serializers.CharField()
    start_date = serializers.DateTimeField()
    commission = CommissionSerializer()
    evaluations = EvaluationWithMakeupSerializer(many=True)
    students = StudentSerializer(many=True)
    classes_amount = serializers.IntegerField()
    minimum_attendance = serializers.FloatField()

    class Meta:
        model = Semester
        fields = ('id', 'year_moment', 'start_date', 'commission', 'evaluations', 'students', 'classes_amount', 'minimum_attendance')


class SemesterPostSerializer(serializers.ModelSerializer):
    year_moment = serializers.ChoiceField(choices=Semester.YearMoment.values)
    start_date = serializers.DateTimeField()
    commission = serializers.IntegerField()
    classes_amount = serializers.IntegerField(required=False, min_value=1, default=16)
    minimum_attendance = serializers.FloatField(required=False, default=0.0)

    class Meta:
        model = Semester
        fields = ('year_moment', 'start_date', 'commission', 'classes_amount', 'minimum_attendance')

    def validate_minimum_attendance(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("minimum_attendance must be between 0 and 100")

        if value > 1:
            return value / 100.0

        return value
