from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.client.guarani_client import GuaraniClient


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
