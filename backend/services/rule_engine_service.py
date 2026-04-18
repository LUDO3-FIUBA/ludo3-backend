from django.utils import timezone
import math

class AttendanceRule:
    def __init__(self, semester):
        self.semester = semester

    def has_requirement(self):
        return self.semester.classes_amount is not None and self.semester.minimum_attendance is not None and self.semester.minimum_attendance > 0

    def max_absences(self):
        required_attendances = math.ceil(self.semester.classes_amount * self.semester.minimum_attendance)
        return self.semester.classes_amount - required_attendances

    def remaining_lectures(self, attendance_qrs):
        return self.semester.classes_amount - len(attendance_qrs)
    
    def get_absences(self, attendance_qrs, student):
        absences = 0
        for attendance_qr in attendance_qrs:
            is_absent = True
            for attendance in attendance_qr.attendances.all():
                if attendance.student_id == student.id:
                    is_absent = False
                    break
            if is_absent:
                absences = absences + 1
        return absences

    def is_passed(self, attendance_qrs, student):
        if not self.has_requirement():
            return True

        absences = self.get_absences(attendance_qrs, student)
        remaining_lectures = self.remaining_lectures(attendance_qrs)
        return absences + remaining_lectures <= self.max_absences()

    def is_failed(self, attendance_qrs, student):
        if not self.has_requirement():
            return False

        return self.get_absences(attendance_qrs, student) > self.max_absences()


class EvaluationChainRule:
    def __init__(self, semester):
        self.semester = semester
        self.evaluation_chains = self._evaluation_chains()

    def _semester_evaluations(self):
        evaluations = self.semester.evaluations
        if hasattr(evaluations, "all"):
            evaluations = evaluations.all()
        return sorted(list(evaluations), key=lambda evaluation: evaluation.end_date)

    def _evaluation_chains(self):
        chains = []

        for evaluation in self._semester_evaluations():
            if not evaluation.is_graded or evaluation.parent_evaluation is not None:
                continue

            chain = [evaluation]
            current_evaluation = evaluation

            while True:
                make_up_evaluation = getattr(current_evaluation, "make_up_evaluation", None)
                if make_up_evaluation is None:
                    break

                chain.append(make_up_evaluation)
                current_evaluation = make_up_evaluation

            chains.append(chain)

        return chains

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
        attendance_rule = AttendanceRule(semester)
        chain_rule = EvaluationChainRule(semester)

        if not attendance_rule.is_passed(attendance_qrs, student):
            return False

        return chain_rule.is_passed(evaluation_submissions)

    def is_student_failed(self, attendance_qrs, evaluation_submissions, student, semester):
        attendance_qrs = list(attendance_qrs)
        evaluation_submissions = list(evaluation_submissions)
        attendance_rule = AttendanceRule(semester)
        chain_rule = EvaluationChainRule(semester)

        if attendance_rule.is_failed(attendance_qrs, student):
            return True

        return chain_rule.is_failed(evaluation_submissions)