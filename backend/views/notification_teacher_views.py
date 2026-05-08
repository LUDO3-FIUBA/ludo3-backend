from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

from backend.models import (CommissionInscription, Notification, Semester,
                            UserNotification)
from backend.permissions import IsTeacher
from backend.serializers.notification_serializer import (
    TeacherNotificationCreateSerializer, TeacherNotificationListSerializer)
from backend.services.audit_log_service import AuditLogService
from backend.views.base_view import BaseViewSet
from backend.views.utils import (get_required_int_query_param,
                                 teacher_not_in_commission_staff)


class NotificationTeacherViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = Notification.objects.all()
    serializer_class = TeacherNotificationListSerializer

    @swagger_auto_schema(
        tags=["Notifications Teacher"],
        operation_summary="Send a notification to all accepted students of a semester",
    )
    def create(self, request):
        serializer = TeacherNotificationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        semester = get_object_or_404(Semester.objects, id=data['semester_id'])

        if teacher_not_in_commission_staff(request.user.teacher, semester.commission):
            return Response(
                {"detail": "Teacher not a member of this semester commission"},
                status=status.HTTP_403_FORBIDDEN,
            )

        accepted_inscriptions = CommissionInscription.objects.filter(
            semester=semester,
            status=CommissionInscription.InscriptionStatus.ACCEPTED,
        ).select_related('student__user')

        target_users = [inscription.student.user for inscription in accepted_inscriptions]
        if not target_users:
            return Response(
                {"detail": "No hay alumnos inscriptos al cuatrimestre."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        notification = Notification.objects.create(
            title=data['title'],
            message=data['message'],
            sender=request.user,
            is_urgent=data.get('is_urgent', False),
            send_push=False,
            send_email=False,
            image=data.get('image'),
            semester=semester,
        )

        UserNotification.objects.bulk_create([
            UserNotification(notification=notification, user=user)
            for user in target_users
        ])

        AuditLogService().log(
            request.user,
            request.user,
            f"Docente envió aviso '{notification.title}' a {len(target_users)} alumnos del cuatrimestre {semester}",
        )

        return Response(
            TeacherNotificationListSerializer(notification, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Notifications Teacher"],
        operation_summary="List notifications sent to a given semester",
    )
    def by_semester(self, request):
        semester_id, error = get_required_int_query_param(request, 'semester_id')
        if error is not None:
            return error

        semester = get_object_or_404(Semester.objects, id=semester_id)

        if teacher_not_in_commission_staff(request.user.teacher, semester.commission):
            return Response(
                {"detail": "Teacher not a member of this semester commission"},
                status=status.HTTP_403_FORBIDDEN,
            )

        notifications = Notification.objects.filter(
            semester=semester
        ).prefetch_related('user_notifications').select_related('sender').order_by('-created_at')

        return Response(
            TeacherNotificationListSerializer(notifications, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
