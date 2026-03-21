from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Final
from ..factories import StudentFactory, TeacherFactory, FinalFactory, FinalExamFactory
from unittest import mock
from backend.services.siu_service import SiuService

class FinalExamTeacherViewsTests(APITestCase):
    def setUp(self) -> None:
        self.student = StudentFactory()
        self.teacher = TeacherFactory()

        self.final = FinalFactory(teacher=self.teacher, status=Final.Status.PENDING_ACT)
        self.final_exam = FinalExamFactory(final=self.final, student=self.student, grade=None)

        self.grade_uri = f"/api/finals/{self.final.id}/final_exams/{self.final_exam.id}/grade/"

    def test_grade(self):
        """
        Should register that the teacher graded the FinalExam and the exam now has a grade
        """
        self.client.force_authenticate(user=self.teacher.user)
        subject_response = {"id": 1, "code": "62.01", "name": "Fisica I", "department_id": 2, "correlatives": []}
        with mock.patch.object(SiuService, "get_subject", return_value=subject_response):
            with mock.patch.object(SiuService, "correlative_subjects", return_value=[]):
                response = self.client.put(self.grade_uri, {"grade": 7}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student"]["id"], self.student.pk)
        self.assertEqual(response.data["grade"], 7)

    def test_grade_invalid_grade(self):
        """
        Should fail indicating that the grade is invalid
        """
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.put(self.grade_uri, {"grade": 70}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['grade'][0], "Ensure this value is less than or equal to 10.")

    def test_grade_not_logged_in(self):
        """
        Should fail if unauthorized
        """
        response = self.client.put(self.grade_uri, {"final": self.final.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_grade_student_logged_in(self):
        """
        Should fail if student tries to grade exam
        """
        self.client.force_authenticate(user=self.student.user)

        response = self.client.put(self.grade_uri, {"final": self.final.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

