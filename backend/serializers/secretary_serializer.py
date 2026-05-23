from rest_framework import serializers

from backend.models import Secretary


class SecretarySerializer(serializers.ModelSerializer):
    """Read serializer for Secretary — used for list and detail responses."""

    subsecretaries = serializers.SerializerMethodField()

    class Meta:
        model = Secretary
        fields = (
            'id', 'name', 'parent_secretary', 'location', 'schedule',
            'contact_info', 'subsecretaries', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'subsecretaries')

    def get_subsecretaries(self, obj):
        """Returns basic info for direct child subsecretaries."""
        qs = obj.subsecretaries.all()
        return SecretaryListSerializer(qs, many=True).data


class SecretaryListSerializer(serializers.ModelSerializer):
    """Minimal serializer used in list views and nested contexts."""

    class Meta:
        model = Secretary
        fields = ('id', 'name', 'parent_secretary', 'location', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class SecretaryWriteSerializer(serializers.ModelSerializer):
    """Write serializer for create/update operations."""

    class Meta:
        model = Secretary
        fields = ('name', 'parent_secretary', 'location', 'schedule', 'contact_info')

    def validate_parent_secretary(self, value):
        if value is not None and value.parent_secretary_id is not None:
            raise serializers.ValidationError(
                "La secretaría padre no puede ser ya una subsecretaría. "
                "Solo se admite un nivel de jerarquía."
            )
        return value

    def validate(self, attrs):
        # When updating, guard against creating a loop: the instance itself
        # cannot be set as its own parent.
        if self.instance is not None:
            parent = attrs.get('parent_secretary', self.instance.parent_secretary)
            if parent is not None and parent.pk == self.instance.pk:
                raise serializers.ValidationError(
                    {'parent_secretary': "Una secretaría no puede ser su propio padre."}
                )
        return attrs
