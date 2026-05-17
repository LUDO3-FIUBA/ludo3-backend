from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Commission, Notification, UserNotification
from backend.models.commissionInscription import CommissionInscription
from backend.permissions import IsBedelia
from backend.views.base_view import BaseViewSet


class ClassroomChangeSerializer(serializers.Serializer):
    commission_id = serializers.IntegerField()
    message = serializers.CharField()
    is_urgent = serializers.BooleanField(required=False, default=False)
    send_push = serializers.BooleanField(required=False, default=False)


class BedeliaClassroomChangeViewSet(BaseViewSet):
    """Bedelía endpoint: announce a classroom change for a Commission."""
    queryset = Notification.objects.none()
    serializer_class = ClassroomChangeSerializer
    permission_classes = [IsAuthenticated, IsBedelia]

    @swagger_auto_schema(
        tags=["Bedelia"],
        operation_summary="Listar todas las comisiones (para seleccionar destinatarios)",
    )
    @action(detail=False, methods=['get'], url_path='commissions')
    def commissions(self, request):
        rows = (
            Commission.objects
            .select_related('chief_teacher__user')
            .order_by('subject_name')
            .values('id', 'subject_name', 'siu_id', 'chief_teacher__user__first_name', 'chief_teacher__user__last_name')
        )
        return Response(
            [
                {
                    'id': r['id'],
                    'subject_name': r['subject_name'],
                    'siu_id': r['siu_id'],
                    'chief_teacher_name': f"{r['chief_teacher__user__first_name']} {r['chief_teacher__user__last_name']}".strip(),
                }
                for r in rows
            ],
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        tags=["Bedelia"],
        operation_summary="Anunciar cambio de aula para una comisión",
        request_body=ClassroomChangeSerializer,
    )
    def create(self, request):
        serializer = ClassroomChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        commission = get_object_or_404(Commission, pk=data['commission_id'])

        target_user_ids = self._resolve_recipients(commission)
        if not target_user_ids:
            return Response(
                {"detail": "La comisión no tiene alumnos ni docentes activos para notificar."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        notification = Notification.objects.create(
            title=f"Cambio de aula: {commission.subject_name}",
            message=data['message'],
            sender=request.user,
            is_urgent=data.get('is_urgent', False),
            send_push=data.get('send_push', False),
        )

        UserNotification.objects.bulk_create([
            UserNotification(notification=notification, user_id=uid)
            for uid in target_user_ids
        ])

        return Response(
            {
                "id": notification.id,
                "recipient_count": len(target_user_ids),
                "title": notification.title,
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _resolve_recipients(commission):
        """Students currently accepted into any semester of the commission + the commission's teachers."""
        student_user_ids = set(
            CommissionInscription.objects
            .filter(
                semester__commission=commission,
                status=CommissionInscription.InscriptionStatus.ACCEPTED,
            )
            .values_list('student__user_id', flat=True)
        )
        teacher_user_ids = set(
            commission.teachers.values_list('user_id', flat=True)
        )
        if commission.chief_teacher_id:
            teacher_user_ids.add(commission.chief_teacher.user_id)
        return list(student_user_ids | teacher_user_ids)
