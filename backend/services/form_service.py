import re

from django.core.exceptions import ValidationError
from django.db import transaction

from backend.models.catalog import CatalogItem
from backend.models.form import Form, FormDocumentSource, FormField, FormFieldOption
from backend.models.form_submission import FormAnswer, FormSubmission
from backend.models.form_types import (
    FormFieldType,
    FormProcedureType,
    FormSubmissionStatus,
    FormType,
)

DIGITAL = 'Digital'
DOCUMENTO = 'Documento'


class FormService:

    @transaction.atomic
    def create_form(self, validated_data: dict) -> Form:
        form_type = FormType.objects.get(id=validated_data['form_type_id'])
        form_procedure = FormProcedureType.objects.get(id=validated_data['form_procedure_id'])

        form = Form.objects.create(
            form_name=validated_data['form_name'],
            form_description=validated_data['form_description'],
            form_information=validated_data.get('form_information'),
            form_procedure=form_procedure,
            form_type=form_type,
            requires_teacher_validation=validated_data.get('requires_teacher_validation', False),
        )

        if form_type.form_type_value == DOCUMENTO:
            self._create_documento_form(form, validated_data)
        else:
            self._create_digital_form(form, validated_data)

        return form

    @transaction.atomic
    def update_form(self, form: Form, validated_data: dict) -> Form:
        form_type = FormType.objects.get(id=validated_data['form_type_id'])
        form_procedure = FormProcedureType.objects.get(id=validated_data['form_procedure_id'])

        form.form_name = validated_data['form_name']
        form.form_description = validated_data['form_description']
        form.form_information = validated_data.get('form_information')
        form.form_procedure = form_procedure
        form.form_type = form_type
        form.requires_teacher_validation = validated_data.get('requires_teacher_validation', False)
        form.save()

        FormField.objects.filter(form=form).delete()
        FormDocumentSource.objects.filter(form=form).delete()

        if form_type.form_type_value == DOCUMENTO:
            self._create_documento_form(form, validated_data)
        else:
            self._create_digital_form(form, validated_data)

        return form

    def _create_documento_form(self, form: Form, data: dict):
        document_source = data.get('document_source')
        if not document_source:
            raise ValidationError({'document_source': ['Este campo es obligatorio para formularios tipo Documento.']})

        FormDocumentSource.objects.create(form=form, form_document_source=document_source)

        adjunto_type = FormFieldType.objects.filter(form_field_type_value=FormFieldType.ADJUNTO).first()
        if adjunto_type is None:
            raise ValidationError({'adjunto': [f"El tipo de campo '{FormFieldType.ADJUNTO}' no existe en la base de datos."]})
        FormField.objects.create(
            form=form,
            form_field_label='Adjunto',
            form_field_type=adjunto_type,
            form_field_require=True,
            form_field_order=1,
        )

    def _create_digital_form(self, form: Form, data: dict):
        fields_data = data.get('fields', [])
        if not fields_data:
            raise ValidationError({'fields': ['Un formulario Digital debe tener al menos un campo.']})

        for field_data in fields_data:
            field_type = FormFieldType.objects.get(id=field_data['form_field_type_id'])

            catalog = None
            if field_type.form_field_type_value == FormFieldType.CATALOG:
                catalog_id = field_data.get('catalog_id')
                if not catalog_id:
                    raise ValidationError({'catalog_id': ['El campo de tipo catalog requiere catalog_id.']})
                from backend.models.catalog import Catalog
                try:
                    catalog = Catalog.objects.get(id=catalog_id)
                except Catalog.DoesNotExist:
                    raise ValidationError({'catalog_id': [f'Catálogo {catalog_id} no encontrado.']})

            if field_type.form_field_type_value == FormFieldType.OPTIONS:
                options_data = field_data.get('options', [])
                if not options_data:
                    raise ValidationError({'options': ['Los campos de tipo options requieren al menos una opción.']})

            field = FormField.objects.create(
                form=form,
                form_field_label=field_data['form_field_label'],
                form_field_type=field_type,
                form_field_require=field_data.get('form_field_require', False),
                form_field_order=field_data['form_field_order'],
                catalog=catalog,
            )

            if field_type.form_field_type_value == FormFieldType.OPTIONS:
                for opt in field_data.get('options', []):
                    FormFieldOption.objects.create(
                        form_field=field,
                        form_option_value=opt['form_option_value'],
                        form_option_label=opt['form_option_label'],
                    )

    @transaction.atomic
    def create_digital_submission(self, form: Form, user, answers_data: list, teacher=None) -> FormSubmission:
        form_type = form.form_type.form_type_value
        if form_type != DIGITAL:
            raise ValidationError({'form': ['Este formulario no es de tipo Digital.']})

        fields = {f.id: f for f in form.fields.select_related('form_field_type', 'catalog').prefetch_related('options').all()}

        required_field_ids = {fid for fid, f in fields.items() if f.form_field_require}
        answered_field_ids = {a['field_id'] for a in answers_data if a.get('answer_value') not in (None, '')}
        missing = required_field_ids - answered_field_ids
        if missing:
            raise ValidationError({'answers': [f'Los campos obligatorios sin respuesta: {list(missing)}.']})

        sent_status = FormSubmissionStatus.objects.get(
            form_submission_status_value=FormSubmissionStatus.SENT,
        )
        submission = FormSubmission.objects.create(
            form=form,
            user=user,
            status=sent_status,
            teacher=teacher,
            teacher_status=FormSubmission.TEACHER_STATUS_PENDING if teacher else None,
        )

        for answer_data in answers_data:
            field_id = answer_data['field_id']
            if field_id not in fields:
                raise ValidationError({'answers': [f'El campo {field_id} no pertenece a este formulario.']})

            field = fields[field_id]
            answer_value = answer_data.get('answer_value')
            self._validate_answer(field, answer_value)

            FormAnswer.objects.create(
                submission=submission,
                field=field,
                answer_value=answer_value,
            )

        return submission

    def _validate_answer(self, field: FormField, value):
        field_type = field.form_field_type.form_field_type_value

        if value is None or value == '':
            if field.form_field_require:
                raise ValidationError({'answers': [f'El campo "{field.form_field_label}" es obligatorio.']})
            return

        if field_type == FormFieldType.NUMERO:
            try:
                float(value)
            except ValueError:
                raise ValidationError({'answers': [f'El campo "{field.form_field_label}" debe ser numérico.']})

        elif field_type == FormFieldType.PADRON:
            if not isinstance(value, str) or not re.fullmatch(r'\d{5,7}', value):
                raise ValidationError({'answers': [f'El campo "{field.form_field_label}" debe ser un padrón válido (5-7 dígitos).']})

        elif field_type == FormFieldType.MAIL:
            if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', value):
                raise ValidationError({'answers': [f'El campo "{field.form_field_label}" debe ser un email válido.']})

        elif field_type == FormFieldType.OPTIONS:
            valid_ids = set(field.options.values_list('id', flat=True))
            try:
                option_id = int(value)
            except (ValueError, TypeError):
                raise ValidationError({'answers': [f'El campo "{field.form_field_label}" debe ser un ID de opción válido.']})
            if option_id not in valid_ids:
                raise ValidationError({'answers': [f'La opción {value} no es válida para el campo "{field.form_field_label}".']})

        elif field_type == FormFieldType.CATALOG:
            try:
                item_id = int(value)
            except (ValueError, TypeError):
                raise ValidationError({'answers': [f'El campo "{field.form_field_label}" debe ser un ID de item de catálogo válido.']})
            if not CatalogItem.objects.filter(id=item_id, catalog=field.catalog, catalog_item_active=True).exists():
                raise ValidationError({'answers': [f'El item de catálogo {value} no es válido para el campo "{field.form_field_label}".']})

        elif field_type == FormFieldType.CHECKBOX:
            if str(value).lower() not in ('true', 'false'):
                raise ValidationError({'answers': [f'El campo "{field.form_field_label}" debe ser true o false.']})
