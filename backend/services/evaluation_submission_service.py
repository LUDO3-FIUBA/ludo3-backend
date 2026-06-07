from backend.models.evaluation_submission import EvaluationSubmission
from backend.models.teacher import Teacher
from backend.utils import get_current_datetime


class EvaluationSubmissionService:
    def set_grader(self, submission: EvaluationSubmission, teacher: Teacher):
        submission.grader = teacher
        submission.updated_at = get_current_datetime()
        submission.save()

    def set_feedback_text(self, submission: EvaluationSubmission, feedback_text: str):
        submission.feedback_text = feedback_text
        submission.updated_at = get_current_datetime()
        submission.full_clean()
        submission.save()
    
    def set_grade(self, submission: EvaluationSubmission, teacher: Teacher, grade: int, feedback_text: str = None):
        submission.grade = grade
        submission.submission_status = None
        if feedback_text is not None:
            submission.feedback_text = feedback_text
        if submission.grader is None:
            submission.grader = teacher
        submission.updated_at = get_current_datetime()
        submission.full_clean()
        submission.save()

    def set_status(self, submission: EvaluationSubmission, teacher: Teacher, status: str, feedback_text: str = None):
        submission.submission_status = status
        submission.grade = None
        if feedback_text is not None:
            submission.feedback_text = feedback_text
        if submission.grader is None:
            submission.grader = teacher
        submission.updated_at = get_current_datetime()
        submission.full_clean()
        submission.save()