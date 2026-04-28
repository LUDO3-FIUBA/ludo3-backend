from django.db import models
from django.utils import timezone

from .form import Form, FormField
from .form_types import FormSubmissionStatus
from .user import User


class FormSubmission(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions', verbose_name="Formulario")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_submissions', verbose_name="Usuario")
    submitted_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Enviado en")
    status = models.ForeignKey(
        FormSubmissionStatus,
        on_delete=models.PROTECT,
        related_name='submissions',
        verbose_name="Estado",
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
