from rest_framework import serializers
from backend.models import Evaluation, Semester

from .commission_serializer import CommissionSerializer

class EvaluationSerializer(serializers.ModelSerializer):
    evaluation_name = serializers.CharField()
    is_graded = serializers.BooleanField()
    is_gradeable = serializers.BooleanField()
    parent_evaluation = serializers.IntegerField(source='parent_evaluation_id', allow_null=True)
    passing_grade = serializers.IntegerField(allow_null=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    requires_qr = serializers.BooleanField()
    requires_identity = serializers.BooleanField()

    class Meta:
        model = Evaluation
        fields = ('id', 'evaluation_name', 'is_graded', 'is_gradeable', 'parent_evaluation', 'passing_grade', 'start_date', 'end_date', 'requires_qr', 'requires_identity')


class EvaluationWithMakeupSerializer(serializers.ModelSerializer):
    evaluation_name = serializers.CharField()
    is_graded = serializers.BooleanField()
    is_gradeable = serializers.BooleanField()
    parent_evaluation = serializers.IntegerField(source='parent_evaluation_id', allow_null=True)
    passing_grade = serializers.IntegerField(allow_null=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    requires_qr = serializers.BooleanField()
    requires_identity = serializers.BooleanField()

    class Meta:
        model = Evaluation
        fields = ('id', 'evaluation_name', 'is_graded', 'is_gradeable', 'parent_evaluation', 'passing_grade', 'start_date', 'end_date', 'make_up_evaluation', 'requires_qr', 'requires_identity')
    
    def get_fields(self):
        fields = super(EvaluationWithMakeupSerializer, self).get_fields()
        fields['make_up_evaluation'] = EvaluationWithMakeupSerializer()
        return fields


class SemesterEvaluationsSerializer(serializers.ModelSerializer):
    year_moment = serializers.CharField()
    start_date = serializers.DateTimeField()
    commission = CommissionSerializer()

    class Meta:
        model = Semester
        fields = ('id', 'year_moment', 'start_date', 'commission')


class EvaluationSemesterSerializer(serializers.ModelSerializer):
    evaluation_name = serializers.CharField()
    parent_evaluation = serializers.IntegerField(source='parent_evaluation_id', allow_null=True)
    passing_grade = serializers.IntegerField(allow_null=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    semester = SemesterEvaluationsSerializer()
    requires_qr = serializers.BooleanField()
    requires_identity = serializers.BooleanField()


    class Meta:
        model = Evaluation
        fields = ('id', 'evaluation_name', 'parent_evaluation', 'passing_grade', 'start_date', 'end_date', 'semester', 'requires_qr', 'requires_identity')


class EvaluationPostSerializer(serializers.ModelSerializer):
    semester_id = serializers.IntegerField()
    parent_evaluation = serializers.IntegerField(source='parent_evaluation_id', required=False, allow_null=True)
    evaluation_name = serializers.CharField()
    is_graded = serializers.BooleanField()
    is_gradeable = serializers.BooleanField()
    passing_grade = serializers.IntegerField(allow_null=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    requires_qr = serializers.BooleanField()
    requires_identity = serializers.BooleanField()

    class Meta:
        model = Evaluation
        fields = ('semester_id', 'parent_evaluation', 'evaluation_name', 'is_graded', 'is_gradeable', 'passing_grade', 'start_date', 'end_date', 'requires_qr', 'requires_identity')

    def create(self, validated_data):
        instance = Evaluation(**validated_data)
        instance.save()
        return instance

class EvaluationUpdateSerializer(serializers.ModelSerializer):
    parent_evaluation = serializers.IntegerField(source='parent_evaluation_id', required=False, allow_null=True)

    class Meta:
        model = Evaluation
        fields = (
            "evaluation_name",
            "is_graded",
            "is_gradeable",
            "passing_grade",
            "start_date",
            "end_date",
            "requires_qr",
            "requires_identity",
            "parent_evaluation",
            "semester_id",
        )
        extra_kwargs = {field: {"required": False} for field in fields}

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance