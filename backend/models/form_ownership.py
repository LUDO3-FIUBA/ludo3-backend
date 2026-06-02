from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class FormOwnershipGroup(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Nombre")
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Grupo de propiedad"
        verbose_name_plural = "Grupos de propiedad"
        ordering = ['name']

    def __str__(self):
        return self.name

    def editors(self):
        return self.members.filter(is_editor=True)

    def clean(self):
        if self.pk and not self.members.filter(is_editor=True).exists():
            raise ValidationError(
                "El grupo debe tener al menos un miembro con rol de editor."
            )


class FormOwnershipMember(models.Model):
    DEPARTMENT = 'department'
    SECRETARY = 'secretary'

    ENTITY_TYPE_CHOICES = [
        (DEPARTMENT, 'Departamento'),
        (SECRETARY, 'Secretaría'),
    ]

    group = models.ForeignKey(
        FormOwnershipGroup,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name="Grupo",
    )
    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPE_CHOICES,
        verbose_name="Tipo de entidad",
    )
    entity_id = models.IntegerField(verbose_name="ID de entidad")
    is_editor = models.BooleanField(default=False, verbose_name="Es editor")

    class Meta:
        verbose_name = "Miembro del grupo"
        verbose_name_plural = "Miembros del grupo"
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'entity_type', 'entity_id'],
                name='unique_group_entity',
            )
        ]

    def __str__(self):
        return f"{self.group.name} — {self.entity_type}:{self.entity_id}"
