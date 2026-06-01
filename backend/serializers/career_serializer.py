from rest_framework import serializers

from backend.models.student_career import StudentCareer


class StudentCareerSerializer(serializers.ModelSerializer):
    siu_id = serializers.IntegerField(source='career.siu_id')
    name = serializers.CharField(source='career.name')

    class Meta:
        model = StudentCareer
        fields = ('id', 'siu_id', 'name', 'plan', 'enrollment_date', 'graduation_date')
