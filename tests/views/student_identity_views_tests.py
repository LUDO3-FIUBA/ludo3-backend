from unittest import mock

from django.core import signing
from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories import StudentFactory, TeacherFactory

SIGNING_SALT = 'student-identity'
TOKEN_MAX_AGE = 86400

MY_QR_URL = '/api/student_identity/my_qr/'


def identity_url(token):
    return f'/api/student_identity/identity/{token}/'


class MyQRViewTests(APITestCase):

    def setUp(self):
        self.student = StudentFactory(image='https://s3.example.com/photo.jpg')
        self.teacher = TeacherFactory()

    def test_returns_png_for_authenticated_student(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(MY_QR_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response.content.startswith(b'\x89PNG'))

    def test_requires_authentication(self):
        response = self.client.get(MY_QR_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_for_teacher(self):
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(MY_QR_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class IdentityViewTests(APITestCase):

    def setUp(self):
        self.student = StudentFactory(image='https://s3.example.com/photo.jpg')

    def test_returns_student_data_for_valid_token(self):
        token = signing.dumps({'padron': self.student.padron}, salt=SIGNING_SALT)
        response = self.client.get(identity_url(token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['padron'], self.student.padron)
        self.assertEqual(response.data['first_name'], self.student.user.first_name)
        self.assertEqual(response.data['last_name'], self.student.user.last_name)
        self.assertEqual(response.data['dni'], self.student.user.dni)
        self.assertEqual(response.data['image'], 'https://s3.example.com/photo.jpg')

    def test_returns_404_for_invalid_token(self):
        response = self.client.get(identity_url('token-invalido'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_404_for_expired_token(self):
        token = signing.dumps({'padron': self.student.padron}, salt=SIGNING_SALT)
        with mock.patch(
            'backend.views.student_identity_views.signing.loads',
            side_effect=signing.SignatureExpired,
        ):
            response = self.client.get(identity_url(token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_no_authentication(self):
        token = signing.dumps({'padron': self.student.padron}, salt=SIGNING_SALT)
        response = self.client.get(identity_url(token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_404_for_nonexistent_padron_in_token(self):
        token = signing.dumps({'padron': '0000000'}, salt=SIGNING_SALT)
        response = self.client.get(identity_url(token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
