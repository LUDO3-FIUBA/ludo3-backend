from rest_framework import serializers

from backend.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'location', 'schedule', 'contact_info', 'procedures', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class DepartmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('name', 'location', 'schedule', 'contact_info', 'procedures')
