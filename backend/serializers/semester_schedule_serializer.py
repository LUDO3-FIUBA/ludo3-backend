from rest_framework import serializers
from backend.models import SemesterSchedule


class SemesterScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterSchedule
        fields = ('id', 'day_of_week', 'start_time', 'end_time')
