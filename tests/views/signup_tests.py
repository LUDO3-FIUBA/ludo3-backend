from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Student, Teacher, User
from backend.serializers import user_serializer

SIGNUP_URL = "/auth/users/"


class TeacherSignupTests(APITestCase):
    """Registro como docente: sin Guaraní, requiere legajo, crea Teacher asociado."""

    def setUp(self):
        # Patch the Guaraní lookup so any test path won't accidentally hit it.
        self.guarani_patch = mock.patch.object(
            user_serializer, 'fetch_alumno_email_from_guarani',
            side_effect=AssertionError("Guaraní no debería consultarse en registro de docente"),
        )
        self.guarani_patch.start()

    def tearDown(self):
        self.guarani_patch.stop()

    def _valid_payload(self, **overrides):
        payload = {
            'dni': '40000001',
            'email': 'docente@fi.uba.ar',
            'is_student': False,
            'is_teacher': True,
            'legajo': '12345',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'password': 'secret-pass-1',
        }
        payload.update(overrides)
        return payload

    def test_signup_teacher_ok_creates_user_and_teacher(self):
        response = self.client.post(SIGNUP_URL, self._valid_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        user = User.objects.get(dni='40000001')
        self.assertTrue(user.is_teacher)
        self.assertFalse(user.is_student)
        self.assertEqual(user.email, 'docente@fi.uba.ar')
        self.assertEqual(user.first_name, 'Juan')
        self.assertEqual(user.last_name, 'Perez')

        teacher = Teacher.objects.get(user=user)
        self.assertEqual(teacher.legajo, '12345')
        self.assertEqual(teacher.face_encodings, [])

    def test_signup_teacher_without_legajo_fails(self):
        response = self.client.post(SIGNUP_URL, self._valid_payload(legajo=''), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('legajo', response.data)
        self.assertFalse(User.objects.filter(dni='40000001').exists())

    def test_signup_teacher_without_email_fails(self):
        response = self.client.post(SIGNUP_URL, self._valid_payload(email=''), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_teacher_without_first_name_fails(self):
        response = self.client.post(SIGNUP_URL, self._valid_payload(first_name=''), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)

    def test_signup_teacher_without_last_name_fails(self):
        response = self.client.post(SIGNUP_URL, self._valid_payload(last_name=''), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', response.data)

    def test_signup_cannot_be_student_and_teacher_at_once(self):
        payload = self._valid_payload(is_student=True, padron='123456')
        response = self.client.post(SIGNUP_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('is_teacher', response.data)


class StudentSignupTests(APITestCase):
    """Registro como alumno: hace lookup en Guaraní para obtener email."""

    def test_signup_student_uses_guarani_email(self):
        with mock.patch.object(
            user_serializer, 'fetch_alumno_email_from_guarani',
            return_value='alumno@fi.uba.ar',
        ) as guarani:
            response = self.client.post(SIGNUP_URL, {
                'dni': '40000002',
                'is_student': True,
                'is_teacher': False,
                'padron': '123456',
                'password': 'secret-pass-1',
                'email': 'should-be-ignored@example.com',
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        guarani.assert_called_once_with('40000002')

        user = User.objects.get(dni='40000002')
        self.assertEqual(user.email, 'alumno@fi.uba.ar')
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_teacher)
        self.assertTrue(Student.objects.filter(user=user).exists())
