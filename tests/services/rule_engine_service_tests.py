from datetime import timedelta
import math
from types import SimpleNamespace

from django.test import SimpleTestCase
from django.utils import timezone

from backend.models.evaluation import Evaluation
from backend.models.evaluation_submission import EvaluationSubmission
from backend.models.teacher import Teacher
from backend.services.rule_engine_service import RuleEngineService


class _RelatedItems:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class RuleEngineServiceTests(SimpleTestCase):
    def setUp(self):
        self.next_id = 1

    def _next_id(self):
        current_id = self.next_id
        self.next_id += 1
        return current_id

    def _evaluation(
        self,
        name,
        passing_grade=4,
        is_graded=True,
        is_gradeable=True,
        end_date=None,
        make_up_evaluation=None,
        parent_evaluation=None,
    ):
        return SimpleNamespace(
            id=self._next_id(),
            evaluation_name=name,
            passing_grade=passing_grade,
            is_graded=is_graded,
            is_gradeable=is_gradeable,
            end_date=end_date or timezone.now(),
            make_up_evaluation=make_up_evaluation,
            parent_evaluation=parent_evaluation,
        )

    def _link_makeup_chain(self, *evaluations):
        for parent, child in zip(evaluations, evaluations[1:]):
            parent.make_up_evaluation = child
            child.parent_evaluation = parent

    def _semester_evaluations_ordered(self, evaluations):
        return sorted(list(evaluations), key=lambda evaluation: evaluation.end_date)

    def _evaluation_chains(self, evaluations):
        chains = []

        for evaluation in self._semester_evaluations_ordered(evaluations):
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

    def _semester(self, evaluations, classes_amount=None, minimum_attendance=None):
        return SimpleNamespace(
            classes_amount=classes_amount,
            minimum_attendance=minimum_attendance,
            evaluations=evaluations,
            evaluation_chains=lambda: self._evaluation_chains(evaluations),
            has_attendance_requirement=lambda: (
                classes_amount is not None and
                minimum_attendance is not None and
                minimum_attendance > 0
            ),
            max_absences=lambda: classes_amount - math.ceil(classes_amount * minimum_attendance),
        )

    def _evaluation_model(self, evaluation):
        model = Evaluation()
        model.id = evaluation.id
        model.evaluation_name = evaluation.evaluation_name
        model.passing_grade = evaluation.passing_grade
        model.is_graded = evaluation.is_graded
        model.is_gradeable = evaluation.is_gradeable
        model.end_date = evaluation.end_date
        return model

    def _teacher_model(self, teacher_id):
        teacher = Teacher()
        teacher.id = teacher_id
        return teacher

    def _submission(self, evaluation, grade=None, submission_status=None, grader=None):
        submission = EvaluationSubmission()
        submission.evaluation = self._evaluation_model(evaluation)
        submission.evaluation_id = evaluation.id
        submission.grade = grade
        submission.submission_status = submission_status
        submission.grader = self._teacher_model(grader.id) if grader is not None else None
        return submission

    def _attendance_qr(self, student_ids):
        return SimpleNamespace(
            attendances=_RelatedItems([SimpleNamespace(student_id=student_id) for student_id in student_ids])
        )

    def test_evaluation_submission_is_passed_for_gradeable_evaluation(self):
        evaluation = Evaluation()
        evaluation.is_gradeable = True
        evaluation.passing_grade = 6
        submission = EvaluationSubmission()
        submission.evaluation = evaluation
        submission.grade = 8
        submission.submission_status = None

        self.assertTrue(submission.is_passed())

    def test_evaluation_submission_is_passed_for_non_gradeable_evaluation(self):
        evaluation = Evaluation()
        evaluation.is_gradeable = False
        evaluation.passing_grade = 6
        submission = EvaluationSubmission()
        submission.evaluation = evaluation
        submission.grade = None
        submission.submission_status = EvaluationSubmission.SubmissionStatus.APROBADO

        self.assertTrue(submission.is_passed())

    def test_is_student_passed_true_when_attendance_and_grades_pass(self):
        service = RuleEngineService()
        semester = self._semester(
            [self._evaluation("Exam 1", passing_grade=6)],
            classes_amount=10,
            minimum_attendance=0.8,
        )

        student = SimpleNamespace(id=10)
        attendance_qrs = [self._attendance_qr([10]) for _ in range(8)]
        submissions = [self._submission(semester.evaluations[0], grade=8, grader=SimpleNamespace(id=1))]

        self.assertTrue(service.is_student_passed(attendance_qrs, submissions, student, semester))

    def test_is_student_passed_false_when_missing_required_evaluation(self):
        service = RuleEngineService()
        semester = self._semester(
            [
                self._evaluation("Exam 1", passing_grade=6),
                self._evaluation("Exam 2", passing_grade=6),
            ],
            classes_amount=10,
            minimum_attendance=0.8,
        )

        student = SimpleNamespace(id=10)
        attendance_qrs = [self._attendance_qr([10]) for _ in range(8)]
        submissions = [self._submission(semester.evaluations[0], grade=7, grader=SimpleNamespace(id=1))]

        self.assertFalse(service.is_student_passed(attendance_qrs, submissions, student, semester))

    def test_is_student_passed_accepts_makeup_submission_in_chain(self):
        service = RuleEngineService()
        root = self._evaluation("Exam 1", passing_grade=6)
        makeup = self._evaluation("Makeup 1", passing_grade=6)
        self._link_makeup_chain(root, makeup)
        semester = self._semester([root, makeup])

        student = SimpleNamespace(id=10)
        submissions = [self._submission(makeup, grade=7, grader=SimpleNamespace(id=1))]

        self.assertTrue(service.is_student_passed([], submissions, student, semester))

    def test_is_student_passed_true_when_attendance_limit_not_exceeded_yet(self):
        service = RuleEngineService()
        semester = self._semester(
            [self._evaluation("Exam 1", passing_grade=4)],
            classes_amount=10,
            minimum_attendance=0.8,
        )

        student = SimpleNamespace(id=10)
        attendance_qrs = [
            self._attendance_qr([]),
            self._attendance_qr([10]),
            self._attendance_qr([10]),
            self._attendance_qr([10]),
            self._attendance_qr([10]),
            self._attendance_qr([10]),
            self._attendance_qr([10]),
        ]
        submissions = [self._submission(semester.evaluations[0], grade=8, grader=SimpleNamespace(id=1))]

        self.assertTrue(service.is_student_passed(attendance_qrs, submissions, student, semester))

    def test_is_student_passed_true_for_non_gradeable_approved_submission(self):
        service = RuleEngineService()
        semester = self._semester([self._evaluation("Practice", is_gradeable=False)])

        student = SimpleNamespace(id=10)
        submissions = [
            self._submission(
                semester.evaluations[0],
                grade=None,
                submission_status=EvaluationSubmission.SubmissionStatus.APROBADO,
                grader=SimpleNamespace(id=1),
            )
        ]

        self.assertTrue(service.is_student_passed([], submissions, student, semester))

    def test_is_student_failed_true_when_attendance_limit_already_exceeded(self):
        service = RuleEngineService()
        semester = self._semester(
            [self._evaluation("Exam 1", passing_grade=4, end_date=timezone.now() - timedelta(days=1))],
            classes_amount=10,
            minimum_attendance=0.8,
        )

        student = SimpleNamespace(id=10)
        attendance_qrs = [
            self._attendance_qr([]),
            self._attendance_qr([]),
            self._attendance_qr([]),
            self._attendance_qr([10]),
            self._attendance_qr([10]),
            self._attendance_qr([10]),
            self._attendance_qr([10]),
        ]
        submissions = [self._submission(semester.evaluations[0], grade=9, grader=SimpleNamespace(id=1))]

        self.assertTrue(service.is_student_failed(attendance_qrs, submissions, student, semester))

    def test_is_student_failed_true_when_closed_evaluation_not_passed(self):
        service = RuleEngineService()
        semester = self._semester(
            [self._evaluation("Exam 1", passing_grade=6, end_date=timezone.now() - timedelta(days=1))]
        )

        student = SimpleNamespace(id=10)
        attendance_qrs = [self._attendance_qr([10]) for _ in range(8)]
        submissions = [self._submission(semester.evaluations[0], grade=2, grader=SimpleNamespace(id=1))]

        self.assertTrue(service.is_student_failed(attendance_qrs, submissions, student, semester))

    def test_is_student_failed_false_when_ungraded_submission_can_still_be_corrected(self):
        service = RuleEngineService()
        semester = self._semester(
            [self._evaluation("Exam 1", passing_grade=6, end_date=timezone.now() - timedelta(days=1))]
        )

        student = SimpleNamespace(id=10)
        attendance_qrs = [self._attendance_qr([10]) for _ in range(8)]
        submissions = [self._submission(semester.evaluations[0], grade=2, grader=None)]

        self.assertFalse(service.is_student_failed(attendance_qrs, submissions, student, semester))

    def test_is_student_failed_false_when_closed_non_gradeable_submission_is_approved(self):
        service = RuleEngineService()
        semester = self._semester(
            [self._evaluation("Practice", is_gradeable=False, end_date=timezone.now() - timedelta(days=1))]
        )

        student = SimpleNamespace(id=10)
        attendance_qrs = [self._attendance_qr([10]) for _ in range(8)]
        submissions = [
            self._submission(
                semester.evaluations[0],
                grade=None,
                submission_status=EvaluationSubmission.SubmissionStatus.APROBADO,
                grader=SimpleNamespace(id=1),
            )
        ]

        self.assertFalse(service.is_student_failed(attendance_qrs, submissions, student, semester))

    def test_get_absences_counts_sessions_without_student(self):
        service = RuleEngineService()
        student = SimpleNamespace(id=99)
        attendance_qrs = [
            self._attendance_qr([99]),
            self._attendance_qr([]),
            self._attendance_qr([1, 2, 3]),
            self._attendance_qr([99, 100]),
            self._attendance_qr([]),
        ]

        self.assertEqual(service.get_absences(attendance_qrs, student), 3)