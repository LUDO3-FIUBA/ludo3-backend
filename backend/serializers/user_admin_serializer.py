from rest_framework import serializers

from backend.models import User


class UserAdminReadSerializer(serializers.ModelSerializer):
    padron = serializers.SerializerMethodField()
    legajo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'dni', 'email', 'first_name', 'last_name',
            'is_student', 'is_teacher', 'is_staff',
            'padron', 'legajo',
        )

    def get_padron(self, obj):
        if obj.is_student and hasattr(obj, 'student'):
            return obj.student.padron
        return None

    def get_legajo(self, obj):
        if obj.is_teacher and hasattr(obj, 'teacher'):
            return obj.teacher.legajo
        return None


class UserAdminWriteSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)
    dni = serializers.CharField(max_length=9, required=False)
    padron = serializers.CharField(max_length=7, required=False)
    legajo = serializers.CharField(max_length=8, required=False)
    promote_to_teacher = serializers.BooleanField(required=False, default=False)
    promote_to_student = serializers.BooleanField(required=False, default=False)
    new_padron = serializers.CharField(max_length=7, required=False)
    new_legajo = serializers.CharField(max_length=8, required=False)
