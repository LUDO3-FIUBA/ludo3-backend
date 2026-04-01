from datetime import datetime, timedelta, timezone

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Evaluation
from tests.factories import CommissionFactory, EvaluationFactory, SemesterFactory, StudentFactory, TeacherFactory


class EvaluationTeacherViewsTests(APITestCase):
    def setUp(self) -> None:
        self.chief_teacher = TeacherFactory()
        self.other_teacher = TeacherFactory()
        self.student = StudentFactory()

        self.commission = CommissionFactory(chief_teacher=self.chief_teacher)
        self.semester = SemesterFactory(commission=self.commission)

        self.evaluation = EvaluationFactory(
            semester=self.semester,
            evaluation_name="Parcial 1",
            is_graded=True,
            passing_grade=4,
            requires_qr=False,
            requires_identity=False,
        )

        self.add_uri = "/api/teacher/evaluations/add_evaluation/"
        self.update_uri = "/api/teacher/evaluations/update_evaluation/"

    def _iso(self, dt: datetime) -> str:
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def test_add_evaluation_success_chief_teacher(self):
        """
        Should create an evaluation when authenticated user is the commission chief teacher.
        """
        self.client.force_authenticate(user=self.chief_teacher.user)

        now = datetime.now(timezone.utc)
        payload = {
            "semester_id": self.semester.id,
            "evaluation_name": "Parcial 2",
            "is_graded": True,
            "is_gradeable": True,
            "passing_grade": 6,
            "start_date": self._iso(now + timedelta(days=1)),
            "end_date": self._iso(now + timedelta(days=2)),
            "requires_qr": True,
            "requires_identity": True,
        }

        response = self.client.post(self.add_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Evaluation.objects.filter(
                semester=self.semester,
                evaluation_name="Parcial 2",
                passing_grade=6,
                requires_qr=True,
                requires_identity=True,
            ).exists()
        )

    def test_add_evaluation_unauthenticated(self):
        """
        Should return 401 if user is not authenticated.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "semester_id": self.semester.id,
            "evaluation_name": "Parcial 3",
            "is_graded": True,
            "is_gradeable": True,
            "passing_grade": 4,
            "start_date": self._iso(now + timedelta(days=1)),
            "end_date": self._iso(now + timedelta(days=2)),
            "requires_qr": False,
            "requires_identity": False,
        }

        response = self.client.post(self.add_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_evaluation_forbidden_for_non_chief_teacher(self):
        """
        Should return 403 when authenticated teacher is not chief teacher.
        """
        self.client.force_authenticate(user=self.other_teacher.user)

        now = datetime.now(timezone.utc)
        payload = {
            "semester_id": self.semester.id,
            "evaluation_name": "Parcial 4",
            "is_graded": True,
            "is_gradeable": True,
            "passing_grade": 4,
            "start_date": self._iso(now + timedelta(days=1)),
            "end_date": self._iso(now + timedelta(days=2)),
            "requires_qr": False,
            "requires_identity": False,
        }

        response = self.client.post(self.add_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_evaluation_forbidden_for_student(self):
        """
        Should return 403 when student tries to create an evaluation.
        """
        self.client.force_authenticate(user=self.student.user)

        now = datetime.now(timezone.utc)
        payload = {
            "semester_id": self.semester.id,
            "evaluation_name": "Parcial 5",
            "is_graded": True,
            "is_gradeable": True,
            "passing_grade": 4,
            "start_date": self._iso(now + timedelta(days=1)),
            "end_date": self._iso(now + timedelta(days=2)),
            "requires_qr": False,
            "requires_identity": False,
        }

        response = self.client.post(self.add_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_evaluation_success_chief_teacher(self):
        """
        Should update an evaluation when authenticated user is the commission chief teacher.
        """
        self.client.force_authenticate(user=self.chief_teacher.user)

        now = datetime.now(timezone.utc)
        payload = {
            "evaluation_id": self.evaluation.id,
            "passing_grade": 7,
            "is_graded": False,
            "is_gradeable": True,
            "requires_qr": True,
            "requires_identity": True,
            "start_date": self._iso(now + timedelta(days=3)),
            "end_date": self._iso(now + timedelta(days=4)),
        }

        response = self.client.put(self.update_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.evaluation.refresh_from_db()
        self.assertEqual(self.evaluation.passing_grade, 7)
        self.assertFalse(self.evaluation.is_graded)
        self.assertTrue(self.evaluation.requires_qr)
        self.assertTrue(self.evaluation.requires_identity)

    def test_update_evaluation_not_found(self):
        """
        Should return 404 when evaluation does not exist.
        """
        self.client.force_authenticate(user=self.chief_teacher.user)

        payload = {"evaluation_id": 999999, "passing_grade": 8}
        response = self.client.put(self.update_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_evaluation_unauthenticated(self):
        """
        Should return 401 if user is not authenticated.
        """
        payload = {"evaluation_id": self.evaluation.id, "passing_grade": 8}
        response = self.client.put(self.update_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_evaluation_forbidden_for_non_chief_teacher(self):
        """
        Should return 403 when authenticated teacher is not chief teacher.
        """
        self.client.force_authenticate(user=self.other_teacher.user)

        payload = {"evaluation_id": self.evaluation.id, "passing_grade": 8}
        response = self.client.put(self.update_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_evaluation_forbidden_for_student(self):
        """
        Should return 403 when student tries to update an evaluation.
        """
        self.client.force_authenticate(user=self.student.user)

        payload = {"evaluation_id": self.evaluation.id, "passing_grade": 8}
        response = self.client.put(self.update_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_evaluation_updates_is_gradeable(self):
        """
        Should update is_gradeable field.
        """
        self.client.force_authenticate(user=self.chief_teacher.user)

        payload = {
            "evaluation_id": self.evaluation.id,
            "is_gradeable": False,
        }

        response = self.client.put(self.update_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.evaluation.refresh_from_db()
        self.assertFalse(self.evaluation.is_gradeable)

    def test_add_evaluation_with_parent_same_semester(self):
        """
        Should create evaluation with parent_evaluation when parent belongs to same semester.
        """
        self.client.force_authenticate(user=self.chief_teacher.user)

        parent = EvaluationFactory(semester=self.semester)
        now = datetime.now(timezone.utc)
        payload = {
            "semester_id": self.semester.id,
            "parent_evaluation": parent.id,
            "evaluation_name": "Recuperatorio Parcial 1",
            "is_graded": True,
            "is_gradeable": True,
            "passing_grade": 6,
            "start_date": self._iso(now + timedelta(days=5)),
            "end_date": self._iso(now + timedelta(days=6)),
            "requires_qr": False,
            "requires_identity": False,
        }

        response = self.client.post(self.add_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Evaluation.objects.get(evaluation_name="Recuperatorio Parcial 1")
        self.assertEqual(created.parent_evaluation_id, parent.id)

    def test_add_evaluation_rejects_parent_from_other_semester(self):
        """
        Should reject parent_evaluation when parent belongs to another semester.
        """
        self.client.force_authenticate(user=self.chief_teacher.user)

        other_semester = SemesterFactory()
        other_parent = EvaluationFactory(semester=other_semester)
        now = datetime.now(timezone.utc)
        payload = {
            "semester_id": self.semester.id,
            "parent_evaluation": other_parent.id,
            "evaluation_name": "Recuperatorio Invalido",
            "is_graded": True,
            "is_gradeable": True,
            "passing_grade": 6,
            "start_date": self._iso(now + timedelta(days=5)),
            "end_date": self._iso(now + timedelta(days=6)),
            "requires_qr": False,
            "requires_identity": False,
        }

        response = self.client.post(self.add_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_evaluation", response.data)

    def test_update_evaluation_sets_parent_same_semester(self):
        """
        Should update parent_evaluation when parent belongs to same semester.
        """
        self.client.force_authenticate(user=self.chief_teacher.user)

        parent = EvaluationFactory(semester=self.semester)
        payload = {
            "evaluation_id": self.evaluation.id,
            "parent_evaluation": parent.id,
        }

        response = self.client.put(self.update_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.evaluation.refresh_from_db()
        self.assertEqual(self.evaluation.parent_evaluation_id, parent.id)

    def test_update_evaluation_rejects_parent_from_other_semester(self):
        """
        Should reject parent_evaluation update when parent belongs to another semester.
        """
        self.client.force_authenticate(user=self.chief_teacher.user)

        other_semester = SemesterFactory()
        other_parent = EvaluationFactory(semester=other_semester)
        payload = {
            "evaluation_id": self.evaluation.id,
            "parent_evaluation": other_parent.id,
        }

        response = self.client.put(self.update_uri, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_evaluation", response.data)