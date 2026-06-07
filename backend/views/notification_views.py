from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Notification, Semester, UserNotification
from backend.models.user import User
from backend.serializers.notification_serializer import (
    NotificationCreateSerializer,
    NotificationSerializer,
    UserNotificationSerializer,
)
from backend.views.base_view import BaseViewSet
from backend.views.utils import user_can_view_semester


def _resolve_recipients(recipient_groups, user_ids):
    target_users = User.objects.none()

    if 'all' in recipient_groups:
        target_users = User.objects.all()
    elif recipient_groups:
        q = Q()
        if 'students' in recipient_groups:
            q |= Q(is_student=True)
        if 'teachers' in recipient_groups:
            q |= Q(is_teacher=True)
        if 'staff' in recipient_groups:
            q |= Q(is_staff=True)
        target_users = User.objects.filter(q)

    if user_ids:
        target_users = (target_users | User.objects.filter(id__in=user_ids)).distinct()
    else:
        target_users = target_users.distinct()

    return target_users
class NotificationViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = UserNotificationSerializer

    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Notifications"],
        operation_summary="Get all notifications for the authenticated user",
    )
    def my_notifications(self, request):
        user_notifications = UserNotification.objects.filter(
            user=request.user
        ).select_related('notification')

        return Response(
            UserNotificationSerializer(user_notifications, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['GET'], url_path=r'semester/(?P<semester_id>[^/.]+)')
    @swagger_auto_schema(
        tags=["Notifications"],
        operation_summary="Get notifications for the authenticated user in a semester",
    )
    def by_semester(self, request, semester_id=None):
        semester = get_object_or_404(Semester.objects, id=semester_id)
        if not user_can_view_semester(request.user, semester):
            return Response(
                {"detail": "You do not have access to this semester's notifications."},
                status=status.HTTP_403_FORBIDDEN,
            )

        notifications = Notification.objects.filter(
            semester=semester
        ).select_related('sender', 'semester__commission').order_by('-created_at')

        return Response(
            NotificationSerializer(notifications, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['PATCH', 'POST'])
    @swagger_auto_schema(
        tags=["Notifications"],
        operation_summary="Mark a notification as read",
    )
    def mark_as_read(self, request, pk=None):
        user_notification = get_object_or_404(
            UserNotification.objects,
            pk=pk,
            user=request.user,
        )

        user_notification.is_read = True
        user_notification.save()

        return Response(
            UserNotificationSerializer(user_notification, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['DELETE'])
    @swagger_auto_schema(
        tags=["Notifications"],
        operation_summary="Delete a notification for the authenticated user",
    )
    def delete_for_me(self, request, pk=None):
        user_notification = get_object_or_404(
            UserNotification.objects,
            pk=pk,
            user=request.user,
        )
        user_notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    @swagger_auto_schema(
        tags=["Notifications"],
        operation_summary="Create a notification and send it to the specified users or groups",
    )
    def create_notification(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user_ids = data.pop('user_ids')
        recipient_groups = data.pop('recipient_groups')

        if user_ids:
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

        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
