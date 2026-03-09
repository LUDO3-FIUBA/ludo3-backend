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
    file = serializers.FileField(use_url=False)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    class Meta:
        model = EvaluationSubmission
        fields = (
            'evaluation', 'student', 'grade', 'grader',
            'file', 'submission_url', 'submission_text',
            'created_at', 'updated_at'
        )

class EvaluationSubmissionWithMakeupSerializer(serializers.ModelSerializer):
    evaluation = EvaluationWithMakeupSerializer()
    student = StudentSerializer()
    grade = serializers.IntegerField()
    grader = TeacherSerializer()
    file = serializers.FileField(use_url=False)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    class Meta:
        model = EvaluationSubmission
        fields = (
            'evaluation', 'student', 'grade', 'grader',
            'file', 'submission_url', 'submission_text',
            'created_at', 'updated_at'
        )

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
        fields = ('evaluation', 'student', 'file', 'submission_url', 'submission_text')


class EvaluationSubmissionCorrectionSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    grade = serializers.IntegerField()
    grader = TeacherSerializer()

    class Meta:
        model = EvaluationSubmission
        fields = ('student', 'grade', 'grader')
