from rest_framework import serializers

from backend.models.catedra_calendar_entry import CatedraCalendarEntry


class CatedraCalendarEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CatedraCalendarEntry
        fields = ('id', 'semester_id', 'date', 'class_number', 'topic', 'entry_type', 'links', 'notes')
