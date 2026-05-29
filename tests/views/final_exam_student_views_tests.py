from unittest import mock

from backend.models.final import Final
from rest_framework import status
from rest_framework.test import APITestCase

from backend.services.image_validator_service import ImageValidatorService
from backend.services.siu_service import SiuService
from ..factories import StudentFactory, TeacherFactory, FinalFactory


class StudentFinalExamViewsTests(APITestCase):
    def setUp(self) -> None:
        self.student = StudentFactory()
        self.teacher = TeacherFactory()

        self.final = FinalFactory(teacher=self.teacher, status=Final.Status.OPEN)

        self.student.face_encodings = [0.1]
        self.student.save()

        self.take_exam_uri = "/api/final_exams/take_exam/"

        self.subject_response = {
            "id": 1,
            "code": "62.01",
            "name": "Física I",
            "department_id": 2,
            "correlatives": []
        }

    def test_take_exam(self):
        """
        Should register that the student took the exam and has a FinalExam for him.
        """
        self.client.force_authenticate(user=self.student.user)

        with mock.patch.object(ImageValidatorService, "validate_identity", lambda x, y: True):
            with mock.patch.object(SiuService, "get_subject", lambda x, y: self.subject_response):
                response = self.client.post(self.take_exam_uri, {"final": self.final.qrid, "image": 'fake_b64'}, format='json')

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(response.data['student'], self.student.pk)
                self.assertEqual(response.data['grade'], None)

                self.assertEqual(self.final.final_exams.count(), 1)
                self.assertEqual(self.final.final_exams.first().student, self.student)

    def test_take_exam_twice(self):
        """
        Should fail if student tries to take the same exam twice.
        """
        self.client.force_authenticate(user=self.student.user)

        with mock.patch.object(ImageValidatorService, "validate_identity", lambda x, y: True):
            with mock.patch.object(SiuService, "get_subject", lambda x, y: self.subject_response):
                self.client.post(self.take_exam_uri, {"final": self.final.qrid, "image": 'fake_b64'}, format='json')
                response = self.client.post(self.take_exam_uri, {"final": self.final.qrid, "image": 'fake_b64'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_take_exam_not_logged_in(self):
        """
        Should fail if unauthorized
        """
        response = self.client.post(self.take_exam_uri, {"final": self.final.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_take_exam_teacher_logged_in(self):
        """
        Should fail if teacher tries to take an exam
        """
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.post(self.take_exam_uri, {"final": self.final.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_take_exam_incorrect_validation(self):
        """
        Should fail if student is not properly validated
        """
        pass
