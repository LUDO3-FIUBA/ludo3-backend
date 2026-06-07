from rest_framework import serializers

from backend.models import Contact, Student


class StudentContactSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Student
        fields = ('padron', 'full_name', 'email')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class StudentContactProfileSerializer(StudentContactSerializer):
    linkedin_url = serializers.CharField(source='user.linkedin_url', allow_blank=True, default='')
    github_url = serializers.CharField(source='user.github_url', allow_blank=True, default='')
    profile_photo = serializers.CharField(source='user.profile_photo', allow_null=True, default=None)

    class Meta(StudentContactSerializer.Meta):
        fields = StudentContactSerializer.Meta.fields + ('linkedin_url', 'github_url', 'profile_photo')


class ContactSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    is_sender = serializers.SerializerMethodField()
    id = serializers.IntegerField()

    class Meta:
        model = Contact
        fields = ('id', 'contact', 'status', 'is_sender', 'created_at')

    def get_contact(self, obj):
        requesting_student = self.context.get('student')
        other = obj.to_student if obj.from_student == requesting_student else obj.from_student
        if obj.status == Contact.Status.ACCEPTED:
            return StudentContactProfileSerializer(other).data
        return StudentContactSerializer(other).data

    def get_is_sender(self, obj):
        requesting_student = self.context.get('student')
        return obj.from_student == requesting_student
