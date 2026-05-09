from rest_framework import serializers

from backend.models import CommissionInscription

from .commission_serializer import CommissionSerializer
from .semester_serializer import SemesterSerializer


class CommissionInscriptionSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer()
    status = serializers.CharField()

    class Meta:
        model = CommissionInscription
        fields = ('semester', 'status')

class CommissionInscriptionPostSerializer(serializers.ModelSerializer):
    semester = serializers.IntegerField()
    student = serializers.IntegerField()

    class Meta:
        model = CommissionInscription
        fields = ('semester', 'student')


class SemesterCurrentInscriptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    year_moment = serializers.CharField()
    start_date = serializers.DateTimeField()
    commission = CommissionSerializer()
    classes_amount = serializers.IntegerField()
    minimum_attendance = serializers.FloatField()
    max_absences = serializers.SerializerMethodField()

    def get_max_absences(self, obj):
        if not obj.has_attendance_requirement():
            return None
        return obj.max_absences()


class CommissionInscriptionCurrentSerializer(serializers.ModelSerializer):
    semester = SemesterCurrentInscriptionSerializer()
    status = serializers.CharField()

    class Meta:
        model = CommissionInscription
        fields = ('semester', 'status')
