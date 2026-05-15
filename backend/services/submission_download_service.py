from django.http import FileResponse
from django.core.exceptions import PermissionDenied
from backend.models import EvaluationSubmission
from backend.models.teacher import Teacher
from backend.views.utils import teacher_not_in_commission_staff


class SubmissionDownloadService:

    @staticmethod
    def get_download(submission: EvaluationSubmission, user):
        if not submission.submission_file:
            raise PermissionDenied("Submission has no file attached.")

        is_owner_student = hasattr(user, 'student') and submission.student.user_id == user.id

        is_staff_teacher = False
        if hasattr(user, 'teacher'):
            try:
                teacher = Teacher.objects.get(user_id=user.id)
            except Teacher.DoesNotExist:
                teacher = None

            if teacher is not None:
                commission = submission.evaluation.semester.commission
                is_staff_teacher = not teacher_not_in_commission_staff(teacher, commission)

        if not (is_owner_student or is_staff_teacher):
            raise PermissionDenied("You do not have permission to download this submission.")

        return SubmissionDownloadService._build_file_response(submission)

    @staticmethod
    def _build_file_response(submission: EvaluationSubmission):
        file_obj = submission.submission_file.open('rb')
        filename = submission.original_filename or 'submission'
        
        response = FileResponse(file_obj, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
