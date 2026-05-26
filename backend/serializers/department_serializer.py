from rest_framework import serializers

from backend.models import Department
from backend.models.form_ownership import FormOwnershipMember


class DepartmentSerializer(serializers.ModelSerializer):
    ownership_groups = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('id', 'name', 'location', 'schedule', 'contact_info', 'procedures', 'ownership_groups', 'created_at', 'updated_at')
        read_only_fields = ('id', 'ownership_groups', 'created_at', 'updated_at')

    def get_ownership_groups(self, obj):
        members = (
            FormOwnershipMember.objects
            .filter(entity_type=FormOwnershipMember.DEPARTMENT, entity_id=obj.id)
            .select_related('group')
        )
        return [
            {'group_id': m.group_id, 'group_name': m.group.name, 'is_editor': m.is_editor}
            for m in members
        ]


class DepartmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('name', 'location', 'schedule', 'contact_info', 'procedures')
