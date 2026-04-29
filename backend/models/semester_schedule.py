from django.db import models
from .semester import Semester


class SemesterSchedule(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY    = 0, 'Lunes'
        TUESDAY   = 1, 'Martes'
        WEDNESDAY = 2, 'Miércoles'
        THURSDAY  = 3, 'Jueves'
        FRIDAY    = 4, 'Viernes'
        SATURDAY  = 5, 'Sábado'

    semester   = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DayOfWeek.choices, verbose_name="Día")
    start_time  = models.TimeField(verbose_name="Hora de inicio")
    end_time    = models.TimeField(verbose_name="Hora de fin")

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')}"
