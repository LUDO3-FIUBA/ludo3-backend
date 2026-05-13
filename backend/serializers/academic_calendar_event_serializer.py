from rest_framework import serializers

from backend.models.academic_calendar_event import AcademicCalendarEvent


class AcademicCalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendarEvent
        fields = ('id', 'name', 'start_date', 'end_date', 'category', 'year', 'is_deadline')
