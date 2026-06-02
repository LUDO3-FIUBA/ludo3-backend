from django.db import models

from .semester import Semester


class CatedraCalendarEntry(models.Model):
    class EntryType(models.TextChoices):
        CLASS       = 'class',       'Clase'
        TP_DELIVERY = 'tp_delivery', 'Entrega TP'
        EXAM        = 'exam',        'Parcial'
        HOLIDAY     = 'holiday',     'Feriado'
        OTHER       = 'other',       'Otro'

    semester     = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='catedra_calendar')
    date         = models.DateField(verbose_name="Fecha")
    class_number = models.IntegerField(null=True, blank=True, verbose_name="Número de clase")
    topic        = models.CharField(max_length=500, verbose_name="Tema")
    entry_type   = models.CharField(
        max_length=20,
        choices=EntryType.choices,
        default=EntryType.CLASS,
        verbose_name="Tipo",
    )
    links = models.JSONField(default=list, blank=True, verbose_name="Links")  # [{label, url}]
    notes = models.TextField(blank=True, default='', verbose_name="Notas")

    class Meta:
        verbose_name = "Entrada del Calendario de Cátedra"
        verbose_name_plural = "Entradas del Calendario de Cátedra"
        ordering = ['date', 'class_number']

    def __str__(self):
        prefix = f"Clase {self.class_number} — " if self.class_number else ""
        return f"{self.semester} · {self.date} · {prefix}{self.topic}"
