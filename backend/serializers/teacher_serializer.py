from rest_framework import serializers

from backend.models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    dni = serializers.CharField(source='user.dni')
    email = serializers.CharField(source='user.email')
    github_url = serializers.URLField(source='user.github_url')

    class Meta:
        model = Teacher
        fields = ('id', 'first_name', 'last_name', 'dni', 'email', 'github_url', 'legajo')
