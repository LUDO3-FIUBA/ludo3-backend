from django.db import models
from django.utils import timezone

from .form import Form, FormField
from .form_types import FormSubmissionStatus
from .user import User


class FormSubmission(models.Model):
    TEACHER_STATUS_PENDING = 'pending'
    TEACHER_STATUS_APPROVED = 'approved'
    TEACHER_STATUS_DENIED = 'denied'
    TEACHER_STATUS_CHOICES = [
        (TEACHER_STATUS_PENDING, 'Pendiente'),
        (TEACHER_STATUS_APPROVED, 'Aprobado'),
        (TEACHER_STATUS_DENIED, 'Rechazado'),
    ]

    RECIPIENT_ENTITY_DEPARTMENT = 'department'
    RECIPIENT_ENTITY_SECRETARY = 'secretary'
    RECIPIENT_ENTITY_CHOICES = [
        (RECIPIENT_ENTITY_DEPARTMENT, 'Departamento'),
        (RECIPIENT_ENTITY_SECRETARY, 'Secretaría'),
    ]

    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions', verbose_name="Formulario")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_submissions', verbose_name="Usuario")
    submitted_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Enviado en")
    status = models.ForeignKey(
        FormSubmissionStatus,
        on_delete=models.PROTECT,
        related_name='submissions',
        verbose_name="Estado",
    )
    teacher = models.ForeignKey(
        'Teacher',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='form_validations',
        verbose_name="Docente validador",
    )
    teacher_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=TEACHER_STATUS_CHOICES,
        verbose_name="Estado de validación docente",
    )
    teacher_comment = models.TextField(null=True, blank=True, verbose_name="Comentario del docente")
    # Destinatario único seleccionado por el alumno al enviar.
    # Si el grupo tiene un solo miembro, se completa automáticamente.
    recipient_entity_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=RECIPIENT_ENTITY_CHOICES,
        verbose_name="Tipo de destinatario",
    )
    recipient_entity_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID del destinatario",
    )

    class Meta:
        verbose_name = "Respuesta de formulario"
        verbose_name_plural = "Respuestas de formulario"

    def __str__(self):
        return f"{self.form.form_name} — {self.user}"


class FormAnswer(models.Model):
    submission = models.ForeignKey(
        FormSubmission, on_delete=models.CASCADE, related_name='answers', verbose_name="Respuesta"
    )
    field = models.ForeignKey(
        FormField, on_delete=models.CASCADE, related_name='answers', verbose_name="Campo"
    )
    # For 'options': stores form_option_id as string.
    # For 'catalog': stores catalog_item_id as string.
    # For 'adjunto': will store Firebase Storage URL once integrated (currently null).
    answer_value = models.TextField(null=True, blank=True, verbose_name="Valor de respuesta")

    class Meta:
        verbose_name = "Respuesta de campo"
        verbose_name_plural = "Respuestas de campo"

    def __str__(self):
        return f"{self.submission} — {self.field.form_field_label}: {self.answer_value}"
