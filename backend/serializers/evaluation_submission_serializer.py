from rest_framework import serializers

from backend.models import EvaluationSubmission

from .evaluation_serializer import (EvaluationSerializer,
                                    EvaluationWithMakeupSerializer)
from .student_serializer import StudentSerializer
from .teacher_serializer import TeacherSerializer


class EvaluationSubmissionSerializer(serializers.ModelSerializer):
    evaluation = EvaluationSerializer()
    student = StudentSerializer()
    grade = serializers.IntegerField()
    grader = TeacherSerializer()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    class Meta:
        model = EvaluationSubmission
        fields = ('evaluation', 'student', 'grade', 'grader', 'created_at', 'updated_at')

    def validate(self, attrs):
        file = attrs.get("file") or getattr(self.instance, "file", None)
        url = attrs.get("submission_url") or getattr(self.instance, "submission_url", None)
        text = attrs.get("submission_text") or getattr(self.instance, "submission_text", None)

        if not any([file, url, text]):
            raise serializers.ValidationError(
                "Provide at least one of: file, submission_url, submission_text."
            )
        return attrs

class EvaluationSubmissionWithMakeupSerializer(serializers.ModelSerializer):
    evaluation = EvaluationWithMakeupSerializer()
    student = StudentSerializer()
    grade = serializers.IntegerField()
    grader = TeacherSerializer()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    class Meta:
        model = EvaluationSubmission
        fields = ('evaluation', 'student', 'grade', 'grader', 'created_at', 'updated_at')


class EvaluationSubmissionPutSerializer(serializers.ModelSerializer):

    evaluation = serializers.IntegerField()
    student = serializers.IntegerField()
    grade = serializers.IntegerField()

    class Meta:
        model = EvaluationSubmission
        fields = ('evaluation', 'student', 'grade')



class EvaluationSubmissionPostSerializer(serializers.ModelSerializer):

    evaluation = serializers.IntegerField()
    student = serializers.IntegerField()

    class Meta:
        model = EvaluationSubmission
        fields = ('evaluation', 'student')


class EvaluationSubmissionCorrectionSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    grade = serializers.IntegerField()
    grader = TeacherSerializer()

    class Meta:
        model = EvaluationSubmission
        fields = ('student', 'grade', 'grader')
