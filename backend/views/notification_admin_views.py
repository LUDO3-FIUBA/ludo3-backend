from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from backend.models import Notification, UserNotification
from backend.models.department import Department
from backend.permissions import get_admin_department_id
from backend.serializers.notification_serializer import (
    NotificationAdminSerializer,
    NotificationCreateSerializer,
)
from backend.views.base_view import BaseViewSet
from backend.views.notification_views import _resolve_recipients


class CanPublishNotifications(BasePermission):
    """Super admin o dept admin (no bedelía, no secretaría)."""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        staff = getattr(user, 'staff', None)
        return bool(staff and staff.department_id and not staff.is_bedelia)


class NotificationAdminViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, CanPublishNotifications]
    queryset = Notification.objects.prefetch_related('user_notifications').select_related('department').order_by('-created_at')
    serializer_class = NotificationAdminSerializer

    def _scoped_queryset(self, request):
        qs = self.get_queryset()
        if request.user.is_superuser:
            return qs
        dept_id = get_admin_department_id(request.user)
        if dept_id is None:
            return qs.none()
        return qs.filter(department_id=dept_id)

    @swagger_auto_schema(
        tags=["Notifications Admin"],
        operation_summary="List sent notifications (scoped to caller's department)",
    )
    def list(self, request):
        notifications = self._scoped_queryset(request)
        return Response(
            NotificationAdminSerializer(notifications, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        tags=["Notifications Admin"],
        operation_summary="Create and send a notification",
    )
    def create(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user_ids = data.pop('user_ids')
        recipient_groups = data.pop('recipient_groups')
        requested_department_id = data.pop('department_id', None)

        if request.user.is_superuser:
            department_id = requested_department_id
        else:
            # Dept admin: tag siempre con su propio depto; ignora cualquier override.
            department_id = get_admin_department_id(request.user)

        if department_id is not None and not Department.objects.filter(id=department_id).exists():
            return Response(
                {"department_id": "Departamento inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_ids:
            from backend.models.user import User
            found_ids = set(User.objects.filter(id__in=user_ids).values_list('id', flat=True))
            invalid_ids = [uid for uid in user_ids if uid not in found_ids]
            if invalid_ids:
                return Response(
                    {"non_existent_user_ids": invalid_ids, "detail": "Some user ids do not exist"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

        target_users = _resolve_recipients(recipient_groups, user_ids)
        if not target_users.exists():
            return Response(
                {"detail": "No users found for the given recipients."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        notification = Notification.objects.create(
            title=data['title'],
            message=data['message'],
            sender=request.user,
            is_urgent=data.get('is_urgent', False),
            send_push=data.get('send_push', False),
            send_email=data.get('send_email', False),
            image=data.get('image'),
            department_id=department_id,
        )

        UserNotification.objects.bulk_create([
            UserNotification(notification=notification, user=user)
            for user in target_users
        ])

        return Response(
            NotificationAdminSerializer(notification, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
