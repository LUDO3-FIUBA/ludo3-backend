from datetime import datetime, timezone

from backend.api_exceptions import ValidationError


class EvaluationSubmissionValidator:
    def __init__(self, submission):
        self.submission = submission

    def validate(self):
        self.validate_evaluation_started()
        self.validate_unique_student_submission()
        self.validate_not_graded()

    def validate_evaluation_started(self):
        start_date = self.submission.evaluation.start_date
        if start_date and datetime.now(timezone.utc) < start_date:
            raise ValidationError("Evaluation has not started yet")

    def validate_unique_student_submission(self):
        from backend.models import EvaluationSubmission
        if EvaluationSubmission.objects.filter(evaluation=self.submission.evaluation, student=self.submission.student).exists():
            raise ValidationError(f"Submission already exists for evaluation {self.submission.evaluation.evaluation_name} and student {self.submission.student_id}")
        
    def validate_not_graded(self):
        if self.submission.grade:
            raise ValidationError(f"Evaluation cannot be graded when submitted")
