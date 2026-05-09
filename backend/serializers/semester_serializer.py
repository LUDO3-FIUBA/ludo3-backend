from rest_framework import serializers

from backend.models import Semester

from .commission_serializer import CommissionSerializer
from .evaluation_serializer import (EvaluationSerializer,
                                    EvaluationWithMakeupSerializer)
from .student_serializer import StudentSerializer
from .semester_schedule_serializer import SemesterScheduleSerializer


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
