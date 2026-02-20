from backend.models.evaluation_submission import EvaluationSubmission
from backend.models.teacher import Teacher
from backend.utils import get_current_datetime


class EvaluationSubmissionService:
    def set_grader(self, submission: EvaluationSubmission, teacher: Teacher):
        submission.grader = teacher
        submission.updated_at = get_current_datetime()
        submission.save()
    
    def set_grade(self, submission: EvaluationSubmission, teacher: Teacher, grade: int):
        submission.grade = grade
        submission.grader = teacher
        submission.updated_at = get_current_datetime()
        submission.save()
