from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api_exceptions import ErrorCommunicatingWithExternalSourceError
from backend.client.guarani_client import GuaraniClient
from backend.models import StudentCareer
from backend.models.career import Career
from backend.permissions import IsStudent
from backend.serializers.career_serializer import StudentCareerSerializer
from backend.views.guarani_views import SIU_PAIS_ARGENTINA, SIU_TIPO_DOCUMENTO_DNI


def _parse_siu_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except (ValueError, TypeError):
        return None


def _sync_careers_from_siu(student, dni):
    client = GuaraniClient()

    personas = client.list_personas(
        tipo_documento=SIU_TIPO_DOCUMENTO_DNI,
        numero_documento=dni,
        pais=SIU_PAIS_ARGENTINA,
    )
    if not personas or not isinstance(personas, (list, dict)):
        return None

    persona_id = (personas[0] if isinstance(personas, list) else personas).get('persona')
    if not persona_id:
        return None

    analitico = client.get_persona_datos_analitico(persona_id)
    if not analitico:
        return None
    analitico = analitico if isinstance(analitico, list) else []

    seen = {}
    for item in analitico:
        prop = item.get('propuesta')
        if prop and prop not in seen:
            seen[prop] = {
                'name': item.get('propuesta_nombre', ''),
                'plan': item.get('plan_alumno') or '',
                'enrollment_date': _parse_siu_date(item.get('fecha_ingreso')),
                'graduation_date': _parse_siu_date(item.get('fecha_egreso')),
            }

    for siu_id, data in seen.items():
        career, _ = Career.objects.get_or_create(
            siu_id=siu_id,
            defaults={'name': data['name']},
        )
        StudentCareer.objects.update_or_create(
            student=student,
            career=career,
            defaults={
                'plan': data['plan'],
                'enrollment_date': data['enrollment_date'],
                'graduation_date': data['graduation_date'],
            },
        )

    return StudentCareer.objects.filter(student=student).select_related('career')


class StudentCareerView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @swagger_auto_schema(
        tags=["Careers"],
        operation_summary="Carreras del alumno autenticado",
        operation_description=(
            "Devuelve las carreras del alumno cacheadas en la base de datos. "
            "Si no hay datos locales, consulta el SIU Guaraní y los persiste."
        ),
        responses={
            200: StudentCareerSerializer(many=True),
            404: openapi.Response(description="Alumno no encontrado en el SIU"),
            503: openapi.Response(description="SIU Guaraní no disponible"),
        },
    )
    def get(self, request):
        student = request.user.student
        careers = StudentCareer.objects.filter(student=student).select_related('career')

        if not careers.exists():
            try:
                careers = _sync_careers_from_siu(student, request.user.dni)
            except ErrorCommunicatingWithExternalSourceError:
                return Response(
                    {'detail': 'Error al consultar el SIU Guaraní.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            if careers is None:
                return Response(
                    {'detail': 'Alumno no encontrado en el SIU.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(StudentCareerSerializer(careers, many=True).data)

    @swagger_auto_schema(
        tags=["Careers"],
        operation_summary="Sincronizar carreras del alumno desde el SIU",
        operation_description="Fuerza una re-sincronización de carreras desde el SIU Guaraní.",
        responses={
            200: StudentCareerSerializer(many=True),
            404: openapi.Response(description="Alumno no encontrado en el SIU"),
            503: openapi.Response(description="SIU Guaraní no disponible"),
        },
    )
    def post(self, request):
        student = request.user.student
        try:
            careers = _sync_careers_from_siu(student, request.user.dni)
        except ErrorCommunicatingWithExternalSourceError:
            return Response(
                {'detail': 'Error al consultar el SIU Guaraní.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if careers is None:
            return Response(
                {'detail': 'Alumno no encontrado en el SIU.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(StudentCareerSerializer(careers, many=True).data)
