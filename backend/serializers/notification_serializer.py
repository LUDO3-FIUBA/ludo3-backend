from rest_framework import serializers

from backend.models import Notification, UserNotification


class NotificationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'sender', 'created_at')


class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer()

    class Meta:
        model = UserNotification
        fields = ('id', 'notification', 'is_read')
