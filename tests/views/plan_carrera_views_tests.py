from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from backend.api_exceptions import ErrorCommunicatingWithExternalSourceError
from tests.factories import StudentFactory

URI = '/api/guarani/plan-carrera/'

# Plan 1986: 4-digit numeric SIU codes
ANALITICO_1986 = [
    {'actividad_codigo': '7540', 'actividad_nombre': 'Algoritmos y Programación I', 'nota': '8', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': '7541', 'actividad_nombre': 'Algoritmos y Programación II', 'nota': '7', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': '6103', 'actividad_nombre': 'Análisis Matemático II', 'nota': '9', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': '6103', 'actividad_nombre': 'Análisis Matemático II', 'nota': '4', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': '7540', 'actividad_nombre': 'Algoritmos y Programación I', 'nota': '3', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
]

# Plan 2023: alphanumeric SIU codes
ANALITICO_2023 = [
    {'actividad_codigo': 'CB001', 'actividad_nombre': 'Análisis Matemático II', 'nota': '8', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': 'TB021', 'actividad_nombre': 'Fundamentos de Programación', 'nota': '9', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
    {'actividad_codigo': 'TB025', 'actividad_nombre': 'Paradigmas de Programación', 'nota': '7', 'propuesta': 2, 'propuesta_nombre': 'Ingeniería en Informática'},
]

PERSONA_RESPONSE = [{'persona': 59387, 'email': 'test@fi.uba.ar'}]


class PlanCarreraViewTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.client.force_authenticate(user=self.student.user)

    def _mock_guarani(self, personas=PERSONA_RESPONSE, analitico=ANALITICO_1986):
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

    def test_career_maps_to_fiuba_map_id_plan_1986(self):
        """Plan 1986 (4-digit codes) maps propuesta 2 to 'informatica'."""
        p1, p2 = self._mock_guarani(analitico=ANALITICO_1986)
        with p1, p2:
            response = self.client.get(URI)
        carrera = response.data['carreras'][0]
        self.assertEqual(carrera['propuesta'], 2)
        self.assertEqual(carrera['fiuba_map_carrera_id'], 'informatica')

    def test_career_maps_to_fiuba_map_id_plan_2023(self):
        """Plan 2023 (alphanumeric codes) maps propuesta 2 to 'informatica-2020'."""
        p1, p2 = self._mock_guarani(analitico=ANALITICO_2023)
        with p1, p2:
            response = self.client.get(URI)
        carrera = response.data['carreras'][0]
        self.assertEqual(carrera['propuesta'], 2)
        self.assertEqual(carrera['fiuba_map_carrera_id'], 'informatica-2020')

    def test_plan_1986_codes_converted_to_fiuba_map_format(self):
        """SIU code 7540 must become 75.40 for FIUBA-Map Plan 1986."""
        p1, p2 = self._mock_guarani(analitico=ANALITICO_1986)
        with p1, p2:
            response = self.client.get(URI)
        ids = {m['id'] for m in response.data['materias_aprobadas']}
        self.assertIn('75.40', ids)
        self.assertIn('75.41', ids)
        self.assertIn('61.03', ids)

    def test_plan_2023_codes_mapped_to_fiuba_map_node_ids(self):
        """Alphanumeric SIU codes (Plan 2023) are translated to FIUBA-Map semantic IDs."""
        p1, p2 = self._mock_guarani(analitico=ANALITICO_2023)
        with p1, p2:
            response = self.client.get(URI)
        ids = {m['id'] for m in response.data['materias_aprobadas']}
        self.assertIn('AMII', ids)   # CB001 → AMII
        self.assertIn('FDP', ids)    # TB021 → FDP
        self.assertIn('PDP', ids)    # TB025 → PDP

    def test_failed_exams_excluded(self):
        """Subjects with nota < 4 must not appear."""
        p1, p2 = self._mock_guarani(analitico=ANALITICO_1986)
        with p1, p2:
            response = self.client.get(URI)
        notas = [m['nota'] for m in response.data['materias_aprobadas']]
        self.assertTrue(all(n >= 4 for n in notas))

    def test_duplicate_subject_included_once_per_unique_grade(self):
        """Multiple approved attempts of the same subject appear as separate entries (different grades)."""
        p1, p2 = self._mock_guarani(analitico=ANALITICO_1986)
        with p1, p2:
            response = self.client.get(URI)
        algo1 = [m for m in response.data['materias_aprobadas'] if m['id'] == '75.40']
        self.assertEqual(len(algo1), 1)

    def test_404_when_student_not_in_siu(self):
        p1, p2 = self._mock_guarani(personas=[])
        with p1, p2:
            response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_503_when_guarani_returns_none(self):
        p1, p2 = self._mock_guarani(analitico=None)
        with p1, p2:
            response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_503_when_guarani_raises_on_list_personas(self):
        """Network/timeout error on list_personas must return 503, not 500."""
        from backend.client.guarani_client import GuaraniClient
        with mock.patch.object(GuaraniClient, 'list_personas', side_effect=ErrorCommunicatingWithExternalSourceError):
            response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_503_when_guarani_raises_on_get_analitico(self):
        """Network/timeout error on get_persona_datos_analitico must return 503, not 500."""
        from backend.client.guarani_client import GuaraniClient
        with mock.patch.object(GuaraniClient, 'list_personas', return_value=PERSONA_RESPONSE):
            with mock.patch.object(GuaraniClient, 'get_persona_datos_analitico', side_effect=ErrorCommunicatingWithExternalSourceError):
                response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_unauthenticated_returns_401(self):
        self.client.logout()
        response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_teacher_without_student_returns_403(self):
        from tests.factories import TeacherFactory
        teacher = TeacherFactory()
        self.client.force_authenticate(user=teacher.user)
        response = self.client.get(URI)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
