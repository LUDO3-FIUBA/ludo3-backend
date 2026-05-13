from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from backend.serializers.student_serializer import StudentSerializer
from backend.serializers.teacher_serializer import TeacherSerializer
from backend.serializers.user_serializer import UserCustomGetSerializer
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


class GithubUrlProfileTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.teacher = TeacherFactory()
        self.url = "/auth/users/me/"

    def test_student_can_update_github_url(self):
        self.client.force_authenticate(user=self.student.user)

        response = self.client.patch(
            self.url,
            {"github_url": "https://github.com/student-user"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.user.refresh_from_db()
        self.assertEqual(self.student.user.github_url, "https://github.com/student-user")
        self.assertEqual(response.data["github_url"], "https://github.com/student-user")

    def test_teacher_can_update_github_url(self):
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.patch(
            self.url,
            {"github_url": "https://github.com/teacher-user"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher.user.refresh_from_db()
        self.assertEqual(self.teacher.user.github_url, "https://github.com/teacher-user")
        self.assertEqual(response.data["github_url"], "https://github.com/teacher-user")

    def test_can_clear_github_url(self):
        self.student.user.github_url = "https://github.com/student-user"
        self.student.user.save()
        self.client.force_authenticate(user=self.student.user)

        response = self.client.patch(
            self.url,
            {"github_url": ""},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.user.refresh_from_db()
        self.assertEqual(self.student.user.github_url, "")
        self.assertEqual(response.data["github_url"], "")

    def test_rejects_invalid_github_url(self):
        self.client.force_authenticate(user=self.student.user)

        response = self.client.patch(
            self.url,
            {"github_url": "not-a-url"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("github_url", response.data)

    def test_user_serializer_returns_github_url(self):
        self.student.user.github_url = "https://github.com/current-user"
        self.student.user.save()

        data = UserCustomGetSerializer(self.student.user).data

        self.assertEqual(data["github_url"], "https://github.com/current-user")

    def test_student_serializer_returns_github_url(self):
        self.student.user.github_url = "https://github.com/student-user"
        self.student.user.save()

        data = StudentSerializer(self.student).data

        self.assertEqual(data["github_url"], "https://github.com/student-user")

    def test_teacher_serializer_returns_github_url(self):
        self.teacher.user.github_url = "https://github.com/teacher-user"
        self.teacher.user.save()

        data = TeacherSerializer(self.teacher).data

        self.assertEqual(data["github_url"], "https://github.com/teacher-user")
