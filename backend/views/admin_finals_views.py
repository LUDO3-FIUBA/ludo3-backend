from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Final
from backend.permissions import IsAdmin, get_admin_department_id
from backend.serializers.final_serializer import FinalTeacherListSerializer
from backend.services.audit_log_service import AuditLogService
from backend.services.notification_service import NotificationService
from backend.services.siu_service import SiuService
from backend.views.base_view import BaseViewSet


class AdminFinalsViewSet(BaseViewSet):
    queryset = Final.objects.all()
    serializer_class = FinalTeacherListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def _scoped_queryset(self, request):
        qs = self.get_queryset()
        if request.user.is_superuser:
            return qs
        dept_id = get_admin_department_id(request.user)
        if dept_id is None:
            return qs.none()
        return qs.filter(commissions__department_id=dept_id).distinct()

    @swagger_auto_schema(tags=["Admin Finals"], operation_summary="List finals scoped to caller's department")
    def list(self, request, *args, **kwargs):
        qs = self._scoped_queryset(request)
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(FinalTeacherListSerializer(qs, many=True).data, status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    @swagger_auto_schema(tags=["Admin Finals"], operation_summary="Approve a final date")
    def approve(self, request, pk=None):
        final = self._get_final_or_404(request, pk)

        if final.status != Final.Status.DRAFT:
            return Response(
                {'status': 'Solo se pueden aprobar finales en estado DRAFT.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        siu_final = SiuService().create_final(
            final.teacher.siu_id,
            final.subject_siu_id,
            int(final.date.timestamp()),
        )

        final.siu_id = siu_final["id"]
        final.status = Final.Status.OPEN
        final.save()

        NotificationService().notify_date_approved(final)

        AuditLogService().log(request.user, None, f"Admin aprobó fecha de final: {final}")

        return Response(FinalTeacherListSerializer(final).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    @swagger_auto_schema(tags=["Admin Finals"], operation_summary="Reject a final date")
    def reject(self, request, pk=None):
        final = self._get_final_or_404(request, pk)

        if final.status != Final.Status.DRAFT:
            return Response(
                {'status': 'Solo se pueden rechazar finales en estado DRAFT.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        final.status = Final.Status.REJECTED
        final.save()

        AuditLogService().log(request.user, None, f"Admin rechazó fecha de final: {final}")

        return Response(FinalTeacherListSerializer(final).data, status=status.HTTP_200_OK)

    def _get_final_or_404(self, request, pk):
        try:
            return self._scoped_queryset(request).get(pk=pk)
        except Final.DoesNotExist:
            raise NotFound("Final no encontrado o fuera de tu departamento.")
