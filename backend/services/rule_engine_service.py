from django.utils import timezone

class AttendanceRule:
    def __init__(self, semester):
        self.semester = semester
    
    def get_absences(self, attendance_qrs, student):
        student_id = getattr(student, 'pk', None)
        if student_id is None:
            student_id = getattr(student, 'id', None)

        absences = 0
        for attendance_qr in attendance_qrs:
            is_absent = True
            for attendance in attendance_qr.attendances.all():
                if attendance.student_id == student_id:
                    is_absent = False
                    break
            if is_absent:
                absences = absences + 1
        return absences

    def is_failed(self, attendance_qrs, student):
        if not self.semester.has_attendance_requirement():
            return False

        return self.get_absences(attendance_qrs, student) > self.semester.max_absences()


class EvaluationChainRule:
    def __init__(self, semester):
        self.semester = semester
        self.evaluation_chains = self.semester.evaluation_chains()

    def _submissions_for_chain(self, evaluation_chain, evaluation_submissions):
        evaluation_ids = {evaluation.id for evaluation in evaluation_chain}
        return [submission for submission in evaluation_submissions if submission.evaluation_id in evaluation_ids]

    def chain_has_passing_submission(self, evaluation_chain, evaluation_submissions):
        chain_submissions = self._submissions_for_chain(evaluation_chain, evaluation_submissions)
        return any(submission.is_passed() for submission in chain_submissions)

    def chain_is_closed(self, evaluation_chain):
        current_datetime = timezone.now()
        return all(evaluation.end_date < current_datetime for evaluation in evaluation_chain)

    def chain_is_failed(self, evaluation_chain, evaluation_submissions):
        chain_submissions = self._submissions_for_chain(evaluation_chain, evaluation_submissions)

        if any(submission.grader is None for submission in chain_submissions):
            return False

        return not any(submission.is_passed() for submission in chain_submissions)

    def is_passed(self, evaluation_submissions):
        for evaluation_chain in self.evaluation_chains:
            if not self.chain_has_passing_submission(evaluation_chain, evaluation_submissions):
                return False

        return True

    def is_failed(self, evaluation_submissions):
        for evaluation_chain in self.evaluation_chains:
            if self.chain_is_closed(evaluation_chain) and self.chain_is_failed(evaluation_chain, evaluation_submissions):
                return True

        return False


class RuleEngineService:
    def get_absences(self, attendance_qrs, student):
        return AttendanceRule(None).get_absences(attendance_qrs, student)

    def is_student_passed(self, attendance_qrs, evaluation_submissions, student, semester):
        attendance_qrs = list(attendance_qrs)
        evaluation_submissions = list(evaluation_submissions)
        chain_rule = EvaluationChainRule(semester)

        return chain_rule.is_passed(evaluation_submissions)

    def is_student_failed(self, attendance_qrs, evaluation_submissions, student, semester):
        attendance_qrs = list(attendance_qrs)
        evaluation_submissions = list(evaluation_submissions)
        attendance_rule = AttendanceRule(semester)
        chain_rule = EvaluationChainRule(semester)

        if attendance_rule.is_failed(attendance_qrs, student):
            return True

        return chain_rule.is_failed(evaluation_submissions)