from rest_framework import serializers

from backend.models import Notification, UserNotification
from backend.serializers.image_serializer import AbsoluteImageField


RECIPIENT_GROUPS = ['all', 'students', 'teachers', 'staff']


class TeacherNotificationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    is_urgent = serializers.BooleanField(required=False, default=False)
    image = AbsoluteImageField(required=False, allow_null=True)
    semester_id = serializers.IntegerField()


class TeacherNotificationListSerializer(serializers.ModelSerializer):
    image = AbsoluteImageField(required=False, allow_null=True)
    sender_name = serializers.SerializerMethodField()
    recipient_count = serializers.SerializerMethodField()

    def get_sender_name(self, obj):
        sender = obj.sender
        full_name = f"{sender.first_name} {sender.last_name}".strip()
        return full_name or sender.email

    def get_recipient_count(self, obj):
        return obj.user_notifications.count()

    class Meta:
        model = Notification
        fields = (
            'id', 'title', 'message', 'sender', 'sender_name',
            'created_at', 'is_urgent', 'image', 'recipient_count',
        )


class NotificationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    is_urgent = serializers.BooleanField(required=False, default=False)
    send_push = serializers.BooleanField(required=False, default=False)
    send_email = serializers.BooleanField(required=False, default=False)
    image = AbsoluteImageField(required=False, allow_null=True)
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


YEAR_MOMENT_LABELS = {
    'FS': '1C',
    'SS': '2C',
    'IW': 'Verano',
    'IS': 'Verano',
}


class NotificationSerializer(serializers.ModelSerializer):
    image = AbsoluteImageField(required=False, allow_null=True)
    sender_name = serializers.SerializerMethodField()
    semester_info = serializers.SerializerMethodField()

    def get_sender_name(self, obj):
        sender = obj.sender
        if not sender:
            return None
        full_name = f"{sender.first_name} {sender.last_name}".strip()
        return full_name or sender.email

    def get_semester_info(self, obj):
        semester = obj.semester
        if not semester:
            return None
        moment = YEAR_MOMENT_LABELS.get(semester.year_moment, '')
        year = semester.start_date.year if semester.start_date else ''
        return {
            'subject_name': semester.commission.subject_name,
            'period_label': f"{moment} {year}".strip(),
        }

    class Meta:
        model = Notification
        fields = (
            'id', 'title', 'message', 'sender', 'sender_name', 'created_at',
            'is_urgent', 'send_push', 'send_email', 'image', 'semester_info', 'action_url',
        )


class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer()

    class Meta:
        model = UserNotification
        fields = ('id', 'notification', 'is_read')


class NotificationAdminSerializer(serializers.ModelSerializer):
    image = AbsoluteImageField(required=False, allow_null=True)
    recipient_count = serializers.SerializerMethodField()

    def get_recipient_count(self, obj):
        return obj.user_notifications.count()

    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'sender', 'created_at', 'is_urgent', 'send_push', 'send_email', 'image', 'recipient_count')
