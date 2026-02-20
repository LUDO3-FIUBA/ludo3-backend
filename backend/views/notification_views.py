from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Notification, UserNotification
from backend.models.user import User
from backend.serializers.notification_serializer import (
    NotificationCreateSerializer,
    NotificationSerializer,
)
from backend.views.base_view import BaseViewSet


class NotificationViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationCreateSerializer

    @action(detail=False, methods=['POST'])
    @swagger_auto_schema(
        tags=["Notifications"],
        operation_summary="Create a notification and send it to the specified users",
    )
    def create_notification(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user_ids = data.pop('user_ids')

        users = User.objects.filter(id__in=user_ids)
        found_ids = set(users.values_list('id', flat=True))
        invalid_ids = [uid for uid in user_ids if uid not in found_ids]
        if invalid_ids:
            return Response(
                {"non_existent_user_ids": invalid_ids, "detail": "Some user ids do not exist"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        notification = Notification.objects.create(
            title=data['title'],
            message=data['message'],
            sender=request.user,
        )

        UserNotification.objects.bulk_create([
            UserNotification(notification=notification, user=user)
            for user in users
        ])

        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
