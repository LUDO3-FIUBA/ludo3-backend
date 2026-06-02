from django.db import models
from django.utils import timezone


class Secretary(models.Model):
    """
    Representa una secretaría o subsecretaría dentro de la facultad.

    Un Secretary sin parent_secretary es una secretaría de primer nivel.
    Un Secretary con parent_secretary definido es una subsecretaría.
    La jerarquía se limita a un único nivel (subsecretarías no tienen hijos).
    """

    name = models.CharField(max_length=200, verbose_name="Nombre")
    parent_secretary = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='subsecretaries',
        verbose_name="Secretaría padre",
    )
    location = models.CharField(max_length=300, blank=True, default='', verbose_name="Ubicación")
    schedule = models.TextField(blank=True, default='', verbose_name="Horario de atención")
    contact_info = models.TextField(blank=True, default='', verbose_name="Información de contacto")
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Secretaría"
        verbose_name_plural = "Secretarías"
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        # Prevent sub-subsecretaries: subsecretaries cannot themselves have a parent.
        if self.parent_secretary_id is not None:
            if self.parent_secretary.parent_secretary_id is not None:
                raise ValidationError(
                    "Una subsecretaría no puede tener otra subsecretaría como padre. "
                    "La jerarquía solo admite un nivel de profundidad."
                )
