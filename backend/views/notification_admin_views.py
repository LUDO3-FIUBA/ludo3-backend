from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Notification, UserNotification
from backend.permissions import IsSuperAdmin
from backend.serializers.notification_serializer import (
    NotificationAdminSerializer,
    NotificationCreateSerializer,
)
from backend.views.base_view import BaseViewSet
from backend.views.notification_views import _resolve_recipients


class NotificationAdminViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = Notification.objects.prefetch_related('user_notifications').order_by('-created_at')
    serializer_class = NotificationAdminSerializer

    @swagger_auto_schema(
        tags=["Notifications Admin"],
        operation_summary="List all sent notifications",
    )
    def list(self, request):
        notifications = self.get_queryset()
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
        )

        UserNotification.objects.bulk_create([
            UserNotification(notification=notification, user=user)
            for user in target_users
        ])

        return Response(
            NotificationAdminSerializer(notification, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
