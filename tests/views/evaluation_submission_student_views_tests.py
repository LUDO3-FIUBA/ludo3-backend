from datetime import datetime, timedelta, timezone
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import EvaluationSubmission
from tests.factories import EvaluationFactory, SemesterFactory, StudentFactory, TeacherFactory


class EvaluationSubmissionStudentViewsTests(APITestCase):
    def setUp(self) -> None:
        self.student = StudentFactory()
        self.other_student = StudentFactory()
        self.teacher = TeacherFactory()

        self.semester = SemesterFactory()
        self.semester.students.add(self.student)

        now = datetime.now(timezone.utc)
        self.evaluation = EvaluationFactory(
            semester=self.semester,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )

        self.future_evaluation = EvaluationFactory(
            semester=self.semester,
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=3),
        )

        self.submit_uri = "/api/evaluations/submissions/submit_evaluation/"
        self.my_evaluations_uri = "/api/evaluations/submissions/my_evaluations/"

    def _download_uri(self, submission_id: int) -> str:
        return f"/api/evaluations/submissions/{submission_id}/download-file/"

    def test_submit_evaluation_success(self):
        self.client.force_authenticate(user=self.student.user)

        payload = {
            "evaluation": self.evaluation.id,
            "submission_text": "Mi resolucion",
        }
        response = self.client.post(self.submit_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            EvaluationSubmission.objects.filter(
                evaluation=self.evaluation,
                student=self.student,
                submission_text="Mi resolucion",
            ).exists()
        )

    def test_submit_evaluation_rejects_before_start_date(self):
        self.client.force_authenticate(user=self.student.user)

        payload = {
            "evaluation": self.future_evaluation.id,
            "submission_text": "Entrega anticipada",
        }
        response = self.client.post(self.submit_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Evaluation has not started yet", str(response.data))

    def test_submit_evaluation_forbidden_when_student_not_in_commission(self):
        self.client.force_authenticate(user=self.other_student.user)

        payload = {
            "evaluation": self.evaluation.id,
            "submission_text": "Intento de entrega",
        }
        response = self.client.post(self.submit_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_evaluation_unauthenticated(self):
        payload = {
            "evaluation": self.evaluation.id,
            "submission_text": "Sin auth",
        }
        response = self.client.post(self.submit_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch("backend.views.evaluation_submission_student_views.EvaluationSubmission.full_clean")
    def test_submit_evaluation_returns_400_when_model_validation_fails(self, mocked_full_clean):
        self.client.force_authenticate(user=self.student.user)
        mocked_full_clean.side_effect = ValidationError({"grade": ["invalid"]})

        payload = {
            "evaluation": self.evaluation.id,
            "submission_text": "Mi resolucion",
        }
        response = self.client.post(self.submit_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("grade", response.data)

    def test_my_evaluations_returns_only_logged_student_submissions(self):
        own_submission = EvaluationSubmission.objects.create(
            evaluation=self.evaluation,
            student=self.student,
            submission_text="Entrega propia",
        )

        other_evaluation = EvaluationFactory(semester=self.semester)
        EvaluationSubmission.objects.create(
            evaluation=other_evaluation,
            student=self.other_student,
            submission_text="Entrega ajena",
        )

        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.my_evaluations_uri)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["evaluation"]["id"], own_submission.evaluation_id)

    def test_my_evaluations_unauthenticated(self):
        response = self.client.get(self.my_evaluations_uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_evaluations_forbidden_for_teacher(self):
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(self.my_evaluations_uri)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

