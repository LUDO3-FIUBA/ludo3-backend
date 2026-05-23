from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories import StudentFactory

URI = '/api/guarani/plan-carrera/'

ANALITICO_RESPONSE = [
    {'actividad_codigo': '7540', 'actividad_nombre': 'Algoritmos y Programación I', 'nota': '8', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': '7541', 'actividad_nombre': 'Algoritmos y Programación II', 'nota': '7', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': '6103', 'actividad_nombre': 'Análisis Matemático II', 'nota': '9', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': '6103', 'actividad_nombre': 'Análisis Matemático II', 'nota': '4', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': '7540', 'actividad_nombre': 'Algoritmos y Programación I', 'nota': '3', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': 'CB001', 'actividad_nombre': 'Análisis Matemático II', 'nota': '8', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
]

PERSONA_RESPONSE = [{'persona': 59387, 'email': 'test@fi.uba.ar'}]


class PlanCarreraViewTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.client.force_authenticate(user=self.student.user)

    def _mock_guarani(self, personas=PERSONA_RESPONSE, analitico=ANALITICO_RESPONSE):
        from backend.client.guarani_client import GuaraniClient
        patcher_personas = mock.patch.object(GuaraniClient, 'list_personas', return_value=personas)
        patcher_analitico = mock.patch.object(GuaraniClient, 'get_persona_datos_analitico', return_value=analitico)
        return patcher_personas, patcher_analitico

    def test_returns_career_and_approved_subjects(self):
        p1, p2 = self._mock_guarani()
        with p1, p2:
            response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('carreras', response.data)
        self.assertIn('materias_aprobadas', response.data)

    def test_career_maps_to_fiuba_map_id(self):
        p1, p2 = self._mock_guarani()
        with p1, p2:
            response = self.client.get(URI)
        carrera = response.data['carreras'][0]
        self.assertEqual(carrera['propuesta'], 2)
        self.assertEqual(carrera['fiuba_map_carrera_id'], 'informatica')

    def test_plan_1986_codes_converted_to_fiuba_map_format(self):
        """SIU code 7540 must become 75.40 for FIUBA-Map Plan 1986."""
        p1, p2 = self._mock_guarani()
        with p1, p2:
            response = self.client.get(URI)
        ids = {m['id'] for m in response.data['materias_aprobadas']}
        self.assertIn('75.40', ids)
        self.assertIn('75.41', ids)
        self.assertIn('61.03', ids)

    def test_plan_2020_codes_returned_as_is(self):
        """Alphanumeric SIU codes (Plan 2020) are returned unchanged."""
        p1, p2 = self._mock_guarani()
        with p1, p2:
            response = self.client.get(URI)
        ids = {m['id'] for m in response.data['materias_aprobadas']}
        self.assertIn('CB001', ids)

    def test_failed_exams_excluded(self):
        """Subjects with nota < 4 must not appear."""
        p1, p2 = self._mock_guarani()
        with p1, p2:
            response = self.client.get(URI)
        notas = [m['nota'] for m in response.data['materias_aprobadas']]
        self.assertTrue(all(n >= 4 for n in notas))

    def test_single_approved_subject_returned_once(self):
        """A subject with one approved attempt is returned exactly once."""
        p1, p2 = self._mock_guarani()
        with p1, p2:
            response = self.client.get(URI)
        algo1 = [m for m in response.data['materias_aprobadas'] if m['id'] == '75.40']
        self.assertEqual(len(algo1), 1)

    def test_404_when_student_not_in_siu(self):
        p1, p2 = self._mock_guarani(personas=[])
        with p1, p2:
            response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_503_when_guarani_unavailable(self):
        p1, p2 = self._mock_guarani(analitico=None)
        with p1, p2:
            response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_teacher_without_student_returns_403(self):
        from tests.factories import TeacherFactory
        teacher = TeacherFactory()
        self.client.force_authenticate(user=teacher.user)
        response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
