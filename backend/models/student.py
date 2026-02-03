from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from .user import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    padron = models.CharField(
        max_length=7,
        validators=[
            MinLengthValidator(5),
            RegexValidator(r'^\d{5,7}$', 'El padrón debe ser un número de entre 5 y 7 dígitos')
        ],
        blank=False,
        verbose_name="Padrón"
    )
    inscripto = models.BooleanField(default=False, blank=False)
    face_encodings = ArrayField(base_field=models.FloatField(null=False), blank=False, default=list)
    image = models.CharField(max_length=120, null=True)


    REQUIRED_FIELDS = ['padron']

    def __str__(self):
        return f"{self.user.last_name}, {self.user.first_name} ({self.padron})"

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
