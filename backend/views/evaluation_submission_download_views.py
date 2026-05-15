from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from backend.models import EvaluationSubmission
from backend.services.submission_download_service import SubmissionDownloadService


class EvaluationSubmissionDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        submission = get_object_or_404(EvaluationSubmission, pk=pk)
        return SubmissionDownloadService.get_download(submission, request.user)
