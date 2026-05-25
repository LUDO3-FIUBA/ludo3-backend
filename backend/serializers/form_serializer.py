from rest_framework import serializers

from backend.models.catalog import Catalog, CatalogItem
from backend.models.form import Form, FormDocumentSource, FormField, FormFieldOption
from backend.models.department import Department
from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from backend.models.secretary import Secretary
from backend.models.form_submission import FormAnswer, FormSubmission
from backend.models.form_types import (
    FormFieldType,
    FormSubmissionStatus,
    FormType,
)


# ── Catalog read ─────────────────────────────────────────────────────────────

class CatalogItemSerializer(serializers.ModelSerializer):
    catalog_item_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = CatalogItem
        fields = ['catalog_item_id', 'catalog_item_value', 'catalog_item_label',
                  'catalog_item_order', 'catalog_item_active']


class CatalogSerializer(serializers.ModelSerializer):
    catalog_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Catalog
        fields = ['catalog_id', 'catalog_key', 'catalog_name', 'catalog_description']


class CatalogWithItemsSerializer(serializers.ModelSerializer):
    catalog_id = serializers.IntegerField(source='id', read_only=True)
    items = CatalogItemSerializer(many=True, read_only=True)

    class Meta:
        model = Catalog
        fields = ['catalog_id', 'catalog_key', 'items']


# ── Type catalog read ─────────────────────────────────────────────────────────

class FormOwnershipGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = FormOwnershipGroup
        fields = ['id', 'name']


class FormOwnershipMemberReadSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    parent_secretary_name = serializers.SerializerMethodField()

    class Meta:
        model = FormOwnershipMember
        fields = ['entity_type', 'entity_id', 'is_editor', 'name', 'parent_secretary_name']

    def get_name(self, obj):
        if obj.entity_type == FormOwnershipMember.DEPARTMENT:
            try:
                return Department.objects.get(pk=obj.entity_id).name
            except Department.DoesNotExist:
                return None
        try:
            return Secretary.objects.get(pk=obj.entity_id).name
        except Secretary.DoesNotExist:
            return None

    def get_parent_secretary_name(self, obj):
        if obj.entity_type != FormOwnershipMember.SECRETARY:
            return None
        try:
            sec = Secretary.objects.select_related('parent_secretary').get(pk=obj.entity_id)
            return sec.parent_secretary.name if sec.parent_secretary else None
        except Secretary.DoesNotExist:
            return None


class FormOwnershipGroupWithMembersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    members = FormOwnershipMemberReadSerializer(many=True, read_only=True)

    class Meta:
        model = FormOwnershipGroup
        fields = ['id', 'name', 'members']


class FormTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    value = serializers.CharField(source='form_type_value', read_only=True)

    class Meta:
        model = FormType
        fields = ['id', 'value']


class FormFieldTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    value = serializers.CharField(source='form_field_type_value', read_only=True)

    class Meta:
        model = FormFieldType
        fields = ['id', 'value']


class FormSubmissionStatusSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    value = serializers.CharField(source='form_submission_status_value', read_only=True)

    class Meta:
        model = FormSubmissionStatus
        fields = ['id', 'value']


class SubmissionStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)

    def validate_status(self, value):
        if value not in FormSubmissionStatus.ALL_VALUES:
            raise serializers.ValidationError(
                f"Estado inválido. Valores permitidos: {list(FormSubmissionStatus.ALL_VALUES)}."
            )
        return value


# ── Form read ─────────────────────────────────────────────────────────────────

class FormFieldOptionSerializer(serializers.ModelSerializer):
    form_option_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = FormFieldOption
        fields = ['form_option_id', 'form_option_value', 'form_option_label']


class FormFieldDetailSerializer(serializers.ModelSerializer):
    form_field_id = serializers.IntegerField(source='id', read_only=True)
    form_field_type = FormFieldTypeSerializer(read_only=True)
    options = serializers.SerializerMethodField()
    catalog = serializers.SerializerMethodField()

    class Meta:
        model = FormField
        fields = ['form_field_id', 'form_field_label', 'form_field_type',
                  'form_field_require', 'catalog', 'options']

    def get_options(self, obj):
        if obj.form_field_type.form_field_type_value == FormFieldType.OPTIONS:
            return FormFieldOptionSerializer(obj.options.all(), many=True).data
        return None

    def get_catalog(self, obj):
        if obj.form_field_type.form_field_type_value == FormFieldType.CATALOG and obj.catalog:
            return CatalogWithItemsSerializer(obj.catalog).data
        return None


class FormDocumentSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormDocumentSource
        fields = ['form_document_source']


class FormListSerializer(serializers.ModelSerializer):
    form_id = serializers.IntegerField(source='id', read_only=True)
    ownership_group = FormOwnershipGroupSerializer(read_only=True)
    form_type = FormTypeSerializer(read_only=True)

    class Meta:
        model = Form
        fields = ['form_id', 'form_name', 'form_description', 'ownership_group', 'form_type',
                  'requires_teacher_validation', 'created_at']


class FormDetailSerializer(serializers.ModelSerializer):
    form_id = serializers.IntegerField(source='id', read_only=True)
    ownership_group = FormOwnershipGroupWithMembersSerializer(read_only=True)
    form_type = FormTypeSerializer(read_only=True)
    fields = FormFieldDetailSerializer(many=True, read_only=True)
    document_source = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = ['form_id', 'form_name', 'form_description', 'form_information',
                  'ownership_group', 'form_type', 'requires_teacher_validation', 'fields', 'document_source']

    def get_document_source(self, obj):
        try:
            return obj.document_source.form_document_source
        except FormDocumentSource.DoesNotExist:
            return None


# ── Form create ───────────────────────────────────────────────────────────────

class FormFieldOptionCreateSerializer(serializers.Serializer):
    form_option_value = serializers.CharField(max_length=100)
    form_option_label = serializers.CharField(max_length=200)


class FormFieldCreateSerializer(serializers.Serializer):
    form_field_label = serializers.CharField(max_length=200)
    form_field_type_id = serializers.IntegerField()
    form_field_require = serializers.BooleanField(default=False)
    form_field_order = serializers.IntegerField()
    catalog_id = serializers.IntegerField(allow_null=True, required=False)
    options = FormFieldOptionCreateSerializer(many=True, required=False, default=list)


class FormCreateSerializer(serializers.Serializer):
    form_name = serializers.CharField(max_length=100)
    form_description = serializers.CharField(max_length=300)
    form_information = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    ownership_group_id = serializers.IntegerField()
    form_type_id = serializers.IntegerField()
    requires_teacher_validation = serializers.BooleanField(default=False, required=False)
    document_source = serializers.URLField(allow_null=True, required=False)
    fields = FormFieldCreateSerializer(many=True, required=False, default=list)

    def validate_ownership_group_id(self, value):
        if not FormOwnershipGroup.objects.filter(id=value).exists():
            raise serializers.ValidationError("Grupo de propiedad no encontrado.")
        return value

    def validate_form_type_id(self, value):
        if not FormType.objects.filter(id=value).exists():
            raise serializers.ValidationError("Tipo de formulario no encontrado.")
        return value


# ── Submission create ─────────────────────────────────────────────────────────

class AnswerCreateSerializer(serializers.Serializer):
    field_id = serializers.IntegerField()
    answer_value = serializers.CharField(allow_null=True, allow_blank=True, required=False)


class SubmissionCreateSerializer(serializers.Serializer):
    answers = AnswerCreateSerializer(many=True)
    recipient_entity_type = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    recipient_entity_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_recipient_entity_type(self, value):
        if value and value not in ('department', 'secretary'):
            raise serializers.ValidationError(
                "Tipo de destinatario inválido. Valores permitidos: 'department', 'secretary'."
            )
        return value


# ── Submission read (admin) ───────────────────────────────────────────────────

class FormAnswerReadSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField(source='field.id', read_only=True)
    field_label = serializers.CharField(source='field.form_field_label', read_only=True)

    class Meta:
        model = FormAnswer
        fields = ['field_id', 'field_label', 'answer_value']


class FormSubmissionListSerializer(serializers.ModelSerializer):
    submission_id = serializers.IntegerField(source='id', read_only=True)
    user_id = serializers.CharField(source='user.dni', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    role = serializers.SerializerMethodField()
    student_first_name = serializers.CharField(source='user.first_name', read_only=True)
    student_last_name = serializers.CharField(source='user.last_name', read_only=True)
    student_padron = serializers.SerializerMethodField()
    status = FormSubmissionStatusSerializer(read_only=True)
    answers = FormAnswerReadSerializer(many=True, read_only=True)
    form_id = serializers.IntegerField(source='form.id', read_only=True)
    form_name = serializers.CharField(source='form.form_name', read_only=True)
    form_requires_teacher_validation = serializers.BooleanField(
        source='form.requires_teacher_validation', read_only=True
    )
    teacher_id = serializers.SerializerMethodField()
    teacher_first_name = serializers.SerializerMethodField()
    teacher_last_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = FormSubmission
        fields = [
            'submission_id', 'user_id', 'email', 'first_name', 'last_name', 'role',
            'student_first_name', 'student_last_name', 'student_padron',
            'submitted_at', 'status', 'answers',
            'form_id', 'form_name', 'form_requires_teacher_validation',
            'teacher_id', 'teacher_first_name', 'teacher_last_name',
            'teacher_status', 'teacher_comment',
            'recipient_entity_type', 'recipient_entity_id', 'recipient_name',
        ]

    def get_student_padron(self, obj):
        if obj.user.is_student:
            return obj.user.student.padron
        return None

    def get_role(self, obj):
        if obj.user.is_staff:
            return 'admin'
        if obj.user.is_teacher:
            return 'teacher'
        if obj.user.is_student:
            return 'student'
        return 'unknown'

    def get_teacher_id(self, obj):
        return obj.teacher.user.id if obj.teacher else None

    def get_teacher_first_name(self, obj):
        return obj.teacher.user.first_name if obj.teacher else None

    def get_teacher_last_name(self, obj):
        return obj.teacher.user.last_name if obj.teacher else None

    def get_recipient_name(self, obj):
        if obj.recipient_entity_type == FormOwnershipMember.DEPARTMENT:
            try:
                return Department.objects.get(pk=obj.recipient_entity_id).name
            except Department.DoesNotExist:
                return None
        if obj.recipient_entity_type == FormOwnershipMember.SECRETARY:
            try:
                return Secretary.objects.get(pk=obj.recipient_entity_id).name
            except Secretary.DoesNotExist:
                return None
        return None


class TeacherValidationUpdateSerializer(serializers.Serializer):
    teacher_status = serializers.CharField(max_length=20)
    teacher_comment = serializers.CharField(allow_blank=True, required=False, default='')

    def validate_teacher_status(self, value):
        if value not in ('approved', 'denied'):
            raise serializers.ValidationError(
                "Estado docente inválido. Valores permitidos: 'approved', 'denied'."
            )
        return value
