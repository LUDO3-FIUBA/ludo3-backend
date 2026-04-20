from rest_framework import serializers

from backend.models import Notification, UserNotification


RECIPIENT_GROUPS = ['all', 'students', 'teachers', 'staff']


class NotificationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    is_urgent = serializers.BooleanField(required=False, default=False)
    send_push = serializers.BooleanField(required=False, default=False)
    send_email = serializers.BooleanField(required=False, default=False)
    image = serializers.ImageField(required=False, allow_null=True)
    recipient_groups = serializers.ListField(
        child=serializers.ChoiceField(choices=RECIPIENT_GROUPS),
        required=False,
        default=list,
    )
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
    )

    def validate(self, data):
        if not data.get('recipient_groups') and not data.get('user_ids'):
            raise serializers.ValidationError("Either recipient_groups or user_ids must be provided.")
        return data


class NotificationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'sender', 'created_at', 'is_urgent', 'send_push', 'send_email', 'image')


class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer()

    class Meta:
        model = UserNotification
        fields = ('id', 'notification', 'is_read')


class NotificationAdminSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    recipient_count = serializers.SerializerMethodField()

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_recipient_count(self, obj):
        return obj.user_notifications.count()

    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'sender', 'created_at', 'is_urgent', 'send_push', 'send_email', 'image', 'recipient_count')
