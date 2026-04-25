from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import CommissionInscription
from backend.serializers.commissionInscription_serializer import \
    CommissionInscriptionCurrentSerializer, CommissionInscriptionSerializer
from backend.views.base_view import BaseViewSet
from backend.views.utils import get_current_semester, get_current_year


class CommissionInscriptionViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CommissionInscription.objects.all()
    serializer_class = CommissionInscriptionSerializer

    @swagger_auto_schema(
        tags=["Inscriptions"],
        operation_summary="Gets all semesters the logged in student was inscripted in"
    )
    def list(self, request, *args, **kwargs):
        result = self.get_queryset().filter(student=request.user.student)
        return Response(self.get_serializer(result, many=True).data, status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Inscriptions"],
        operation_summary="Gets current semesters the logged in student is inscripted in"
    )
    @action(detail=False, methods=["GET"])
    def current_inscriptions(self, request):
        all_status = self.get_queryset().filter(
            student=request.user.student,
            semester__start_date__year__gte=get_current_year(),
            semester__year_moment=get_current_semester(),
        ).select_related(
            'semester__commission__chief_teacher__user',
        )
        result = all_status.filter(status__in=["A", "P"])
        return Response(CommissionInscriptionCurrentSerializer(result, many=True).data, status.HTTP_200_OK)
