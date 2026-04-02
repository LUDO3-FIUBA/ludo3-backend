from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    location = models.CharField(max_length=300, blank=True, default='', verbose_name="Ubicación")
    schedule = models.TextField(blank=True, default='', verbose_name="Horario de atención")
    contact_info = models.TextField(blank=True, default='', verbose_name="Información de contacto")
    procedures = models.TextField(blank=True, default='', verbose_name="Trámites")
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['name']

    def __str__(self):
        return self.name
