from django.db import models
from django.core.exceptions import ValidationError

from .department import Department
from .secretary import Secretary
from .user import User


class Staff(models.Model):
    """
    Represents an administrative staff user.

    A Staff instance is associated with EITHER a Department OR a Secretary,
    never both. The `is_bedelia` flag is mutually exclusive with entity
    associations (a bedelía staff is not tied to a Department or Secretary).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department_siu_id = models.IntegerField(db_index=True, default=0, null=False)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admins',
        verbose_name="Departamento",
    )
    secretary = models.ForeignKey(
        Secretary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admins',
        verbose_name="Secretaría",
    )
    is_bedelia = models.BooleanField(default=False, verbose_name="Es bedelía?")

    class Meta:
        verbose_name = "Usuario Administrador"
        verbose_name_plural = "Usuarios Administradores"
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(department__isnull=True) | models.Q(secretary__isnull=True)
                ),
                name='staff_department_or_secretary_not_both',
            )
        ]

    def clean(self):
        if self.department_id is not None and self.secretary_id is not None:
            raise ValidationError(
                "Un Staff no puede estar asociado a un Departamento y a una Secretaría al mismo tiempo."
            )
