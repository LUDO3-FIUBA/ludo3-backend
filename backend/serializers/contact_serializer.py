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


class ContactSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    id = serializers.IntegerField()

    class Meta:
        model = Contact
        fields = ('id', 'contact', 'status', 'created_at')

    def get_contact(self, obj):
        requesting_student = self.context.get('student')
        if obj.from_student == requesting_student:
            return StudentContactSerializer(obj.to_student).data
        return StudentContactSerializer(obj.from_student).data
