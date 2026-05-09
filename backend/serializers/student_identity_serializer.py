from rest_framework import serializers
from backend.models import Student


class StudentIdentitySerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    dni = serializers.CharField(source='user.dni')

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'dni', 'padron', 'image')
