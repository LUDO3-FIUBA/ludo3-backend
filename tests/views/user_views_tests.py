from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from backend.services.image_validator_service import ImageValidatorService
from ..factories import StudentFactory, TeacherFactory


class RegisterFaceTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.url = "/auth/users/register_face/"

    def test_register_face_unauthenticated(self):
        response = self.client.post(self.url, {"image": "fake"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_face_without_image(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_face_success_stores_encodings(self):
        self.client.force_authenticate(user=self.student.user)
        encoding = [0.1] * 128

        with mock.patch.object(ImageValidatorService, "validate_image", return_value=(encoding, None)):
            response = self.client.post(self.url, {"image": "fake_b64"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.face_encodings, encoding)


class FaceRegistrationPendingTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory(face_encodings=[])
        self.teacher = TeacherFactory(face_encodings=[])

    def test_is_me_returns_pending_when_no_encodings(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post("/auth/users/is_me/", {"image": "fake_b64"}, format="json")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data.get("code"), "face_registration_pending")
