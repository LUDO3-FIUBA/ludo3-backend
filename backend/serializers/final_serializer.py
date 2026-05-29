from rest_framework import serializers

from backend.models import Final

from .commission_serializer import CommissionSerializer
from .filterable_model_list_serializer import FilterableModelListSerializer
from .final_exam_serializer import FinalExamTeacherDetailsSerializer


class FinalsListSerializer(FilterableModelListSerializer):
    MODEL = Final

    def to_representation(self, data):
        data = data.filter(**self._filter_params(self.context["filters"])).distinct()
        return super(FinalsListSerializer, self).to_representation(data)


class FinalTeacherSerializer(serializers.ModelSerializer):
    final_exams = FinalExamTeacherDetailsSerializer(many=True)
    commissions = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Final
        fields = ('id', 'subject', 'date', 'qrid', 'status', 'siu_id', 'act', 'final_exams', 'teacher', 'commissions')


class FinalTeacherListSerializer(serializers.ModelSerializer):
    commissions = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Final
        fields = ('id', 'subject', 'date', 'qrid', 'status', 'siu_id', 'act', 'teacher', 'commissions')

