from django.db import models

from .department import Department
from .user import User


class Staff(models.Model):
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
    is_bedelia = models.BooleanField(default=False, verbose_name="Es bedelía?")

    class Meta:
        verbose_name = "Usuario Administrador"
        verbose_name_plural = "Usuarios Administradores"
