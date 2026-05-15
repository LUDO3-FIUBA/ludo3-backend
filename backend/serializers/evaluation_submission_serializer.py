from rest_framework import serializers
from django.urls import reverse

from backend.models import EvaluationSubmission

from .evaluation_serializer import (EvaluationSerializer,
                                    EvaluationWithMakeupSerializer)
from .student_serializer import StudentSerializer
from .teacher_serializer import TeacherSerializer


class EvaluationSubmissionSerializer(serializers.ModelSerializer):
    evaluation = EvaluationSerializer()
    student = StudentSerializer()
    download_url = serializers.SerializerMethodField()
    grade = serializers.IntegerField(required=False, allow_null=True)
    submission_status = serializers.ChoiceField(choices=EvaluationSubmission.SubmissionStatus.choices, required=False, allow_null=True)
    grader = TeacherSerializer()
    feedback_text = serializers.CharField(required=False, allow_null=True)
    original_filename = serializers.CharField(required=False, allow_null=True)
    submission_file = serializers.FileField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    class Meta:
        model = EvaluationSubmission
        fields = (
            'evaluation', 'student', 'grade', 'submission_status', 'grader', 'feedback_text', 'original_filename',
             'submission_text', 'submission_file',
            'download_url', 'created_at', 'updated_at'
        )

    def get_download_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        url = reverse('evaluation-submission-download', kwargs={'pk': obj.pk})
        return request.build_absolute_uri(url) if request else url

class EvaluationSubmissionWithMakeupSerializer(serializers.ModelSerializer):
    evaluation = EvaluationWithMakeupSerializer()
    student = StudentSerializer()
    download_url = serializers.SerializerMethodField()
    grade = serializers.IntegerField(required=False, allow_null=True)
    submission_status = serializers.ChoiceField(choices=EvaluationSubmission.SubmissionStatus.choices, required=False, allow_null=True)
    grader = TeacherSerializer()
    feedback_text = serializers.CharField(required=False, allow_null=True)
    original_filename = serializers.CharField(required=False, allow_null=True)
    submission_file = serializers.FileField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    class Meta:
        model = EvaluationSubmission
        fields = (
            'evaluation', 'student', 'grade', 'submission_status', 'grader', 'feedback_text', 'original_filename',
            'submission_text', 'submission_file',
            'download_url', 'created_at', 'updated_at'
        )

    def get_download_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        url = reverse('evaluation-submission-download', kwargs={'pk': obj.pk})
        return request.build_absolute_uri(url) if request else url

class EvaluationSubmissionPutSerializer(serializers.ModelSerializer):

    evaluation = serializers.IntegerField()
    student = serializers.IntegerField()
    grade = serializers.IntegerField(required=False, allow_null=True)
    submission_status = serializers.ChoiceField(choices=EvaluationSubmission.SubmissionStatus.choices, required=False, allow_null=True)
    feedback_text = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = EvaluationSubmission
        fields = ('evaluation', 'student', 'grade', 'submission_status', 'feedback_text')

    def validate(self, attrs):
        grade = attrs.get('grade', None)
        submission_status = attrs.get('submission_status', None)

        if (grade is None) == (submission_status is None):
            raise serializers.ValidationError({
                'non_field_errors': [
                    'Provide exactly one of grade or submission_status.'
                ]
            })

        return attrs



class EvaluationSubmissionPostSerializer(serializers.ModelSerializer):

    evaluation = serializers.IntegerField()
    student = serializers.IntegerField()
    submission_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = EvaluationSubmission
        fields = ('evaluation', 'student', 'submission_text', 'submission_file')


class EvaluationSubmissionCorrectionSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    download_url = serializers.SerializerMethodField()
    grade = serializers.IntegerField(required=False, allow_null=True)
    grader = TeacherSerializer()
    submission_status = serializers.ChoiceField(choices=EvaluationSubmission.SubmissionStatus.choices, required=False, allow_null=True)
    submission_file = serializers.FileField(required=False, allow_null=True)
    original_filename = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    feedback_text = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = EvaluationSubmission
        fields = ('student', 'grade', 'grader', 'submission_status', 'feedback_text', 'submission_text', 'submission_file', 'original_filename', 'download_url', 'created_at', 'updated_at')

    def get_download_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        url = reverse('evaluation-submission-download', kwargs={'pk': obj.pk})
        return request.build_absolute_uri(url) if request else url
