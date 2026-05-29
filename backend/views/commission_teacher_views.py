from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Commission
from backend.permissions import IsTeacher
from backend.serializers.commission_serializer import (CommissionPutSerializer,
                                                       CommissionSerializer)
from backend.views.base_view import BaseViewSet
from backend.views.utils import get_current_semester, get_current_year


class CommissionTeacherViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = Commission.objects.all()
    serializer_class = CommissionPutSerializer
    
    
    @action(detail=False, methods=["GET"])
    @swagger_auto_schema(
        tags=["Commissions"],
        operation_summary="Get the commissions the logged in teacher is in"
    )
    def my_commissions(self, request):
        result = self.get_queryset().filter(chief_teacher=request.user.teacher).union(self.get_queryset().filter(teachers=request.user.teacher))
        return Response(CommissionSerializer(result, many=True).data, status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"], url_path="shareable_for_final")
    @swagger_auto_schema(
        tags=["Commissions"],
        operation_summary="Commissions in the active semester for the given subject_siu_id (caller must be chief of at least one when creating the final)"
    )
    def shareable_for_final(self, request):
        subject_siu_id = request.query_params.get('subject_siu_id')
        if subject_siu_id is None:
            return Response({'subject_siu_id': 'requerido'}, status=status.HTTP_400_BAD_REQUEST)

        commissions = self.get_queryset().filter(
            subject_siu_id=subject_siu_id,
            semesters__start_date__year=get_current_year(),
            semesters__year_moment=get_current_semester(),
        ).distinct()

        return Response(CommissionSerializer(commissions, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["PUT"])
    @swagger_auto_schema(
        tags=["Commissions"],
        operation_summary="Edit chief tiecher grader weight"
    )
    def chief_teacher_grader_weight(self, request):
        commission: Commission = get_object_or_404(Commission.objects, id=request.data['id'])

        if commission.chief_teacher != request.user.teacher:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        commission.chief_teacher_grader_weight = request.data['chief_teacher_grader_weight']
        commission.save()

        return Response(CommissionSerializer(commission).data, status=status.HTTP_200_OK)
