from django.db import models


class FormType(models.Model):
    form_type_value = models.CharField(max_length=100, verbose_name="Tipo de formulario")

    class Meta:
        verbose_name = "Tipo de formulario"
        verbose_name_plural = "Tipos de formulario"

    def __str__(self):
        return self.form_type_value


class FormFieldType(models.Model):
    form_field_type_value = models.CharField(max_length=100, verbose_name="Tipo de campo")

    TEXTO = 'texto'
    NUMERO = 'numero'
    PADRON = 'padron'
    MAIL = 'mail'
    OPTIONS = 'options'
    CATALOG = 'catalog'
    CHECKBOX = 'checkbox'
    ADJUNTO = 'adjunto'

    class Meta:
        verbose_name = "Tipo de campo de formulario"
        verbose_name_plural = "Tipos de campo de formulario"

    def __str__(self):
        return self.form_field_type_value


class FormSubmissionStatus(models.Model):
    form_submission_status_value = models.CharField(
        max_length=50, unique=True, verbose_name="Estado de respuesta"
    )

    SENT = 'sent'
    PENDING_APPROVAL = 'pending_approval'
    APPROVED = 'approved'
    DENIED = 'denied'

    ALL_VALUES = (SENT, PENDING_APPROVAL, APPROVED, DENIED)

    class Meta:
        verbose_name = "Estado de respuesta"
        verbose_name_plural = "Estados de respuesta"

    def __str__(self):
        return self.form_submission_status_value
