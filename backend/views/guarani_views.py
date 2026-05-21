from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.client.guarani_client import GuaraniClient
from backend.permissions import IsStudent

# Maps SIU propuesta IDs to FIUBA-Map career IDs (pre-2020 plans use numeric SIU codes)
PROPUESTA_TO_FIUBA_MAP = {
    1:   'civil',
    2:   'informatica',
    3:   'alimentos',
    4:   'agrimensura',
    6:   'petroleo',
    7:   'industrial',
    8:   'naval',
    10:  'agrimensura',
    11:  'mecanica',
    12:  'electricista',
    13:  'electronica',
    14:  'quimica',
    15:  'sistemas',
    120: 'electricista',
    126: 'bioingenieria-2020',
}

# Argentine DNI document type and country code in SIU Guaraní
SIU_TIPO_DOCUMENTO_DNI = 0
SIU_PAIS_ARGENTINA = 54


def _siu_code_to_fiuba_map_id(codigo):
    """Converts a 4-digit numeric SIU activity code to FIUBA-Map node ID format.

    SIU Plan 1986 codes are stored as 4-digit integers (e.g. 7540).
    FIUBA-Map Plan 1986 uses the format XX.YY (e.g. 75.40).
    Plan 2020 codes are alphanumeric (e.g. CB001) and returned as-is.
    """
    if codigo and len(codigo) == 4 and codigo.isdigit():
        return f"{codigo[:2]}.{codigo[2:]}"
    return codigo


class PlanCarreraView(APIView):
    """Returns the student's approved subjects and career from SIU Guaraní.

    Used by the FIUBA-Map mobile integration to pre-populate the career graph
    without requiring the student to enter data manually.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    @swagger_auto_schema(
        tags=["Guarani"],
        operation_summary="Plan de carrera del alumno desde Guaraní",
        responses={
            200: openapi.Response(
                description="Materias aprobadas y carrera del alumno",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'carreras': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'propuesta': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'propuesta_nombre': openapi.Schema(type=openapi.TYPE_STRING),
                                    'fiuba_map_carrera_id': openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        ),
                        'materias_aprobadas': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_STRING, description="FIUBA-Map node ID"),
                                    'nota': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        ),
                    },
                ),
            ),
            404: openapi.Response(description="Alumno no encontrado en el SIU"),
            503: openapi.Response(description="SIU Guaraní no disponible"),
        },
    )
    def get(self, request):
        dni = request.user.dni
        client = GuaraniClient()

        personas = client.list_personas(
            tipo_documento=SIU_TIPO_DOCUMENTO_DNI,
            numero_documento=dni,
            pais=SIU_PAIS_ARGENTINA,
        )
        if not personas or not isinstance(personas, (list, dict)):
            return Response(
                {'detail': 'Alumno no encontrado en el SIU.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        persona_id = (personas[0] if isinstance(personas, list) else personas).get('persona')
        if not persona_id:
            return Response(
                {'detail': 'No se pudo obtener el ID de persona del SIU.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        analitico = client.get_persona_datos_analitico(persona_id)
        if analitico is None:
            return Response(
                {'detail': 'Error al consultar el SIU Guaraní.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        analitico = analitico if isinstance(analitico, list) else []

        # Collect unique careers
        propuestas_vistas = {}
        for item in analitico:
            prop = item.get('propuesta')
            if prop and prop not in propuestas_vistas:
                propuestas_vistas[prop] = item.get('propuesta_nombre', '')

        carreras = [
            {
                'propuesta': prop,
                'propuesta_nombre': nombre,
                'fiuba_map_carrera_id': PROPUESTA_TO_FIUBA_MAP.get(prop),
            }
            for prop, nombre in propuestas_vistas.items()
        ]

        # Collect approved subjects (nota >= 4, numeric grade)
        materias_aprobadas = []
        seen = set()
        for item in analitico:
            nota_raw = item.get('nota', '')
            if not (nota_raw and str(nota_raw).isdigit() and int(nota_raw) >= 4):
                continue
            codigo_siu = item.get('actividad_codigo', '')
            fiuba_map_id = _siu_code_to_fiuba_map_id(codigo_siu)
            key = (fiuba_map_id, int(nota_raw))
            if key in seen:
                continue
            seen.add(key)
            materias_aprobadas.append({
                'id': fiuba_map_id,
                'nota': int(nota_raw),
                'nombre': item.get('actividad_nombre', ''),
            })

        return Response({
            'carreras': carreras,
            'materias_aprobadas': materias_aprobadas,
        })


class OfertaComisionesView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Guarani"],
        operation_summary="Lista comisiones con horarios desde Guaraní",
        manual_parameters=[
            openapi.Parameter(
                'actividad_codigo',
                openapi.IN_QUERY,
                description="Código de actividad (materia) para filtrar",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
    )
    def get(self, request):
        actividad_codigo = request.query_params.get('actividad_codigo') or None
        client = GuaraniClient()
        comisiones = client.list_comisiones(actividad_codigo=actividad_codigo) or []
        result = []
        for com in comisiones:
            id_comision = com.get('comision')
            if not id_comision:
                continue
            detail = client.get_comision(id_comision) or {}
            if detail.get('horarios'):
                result.append(detail)
        return Response(result)
