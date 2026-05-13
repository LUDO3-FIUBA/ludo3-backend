from django.db import models


class AcademicCalendarEvent(models.Model):
    class Category(models.TextChoices):
        STUDENT = 'student', 'Estudiantes'
        TEACHER = 'teacher', 'Docentes'
        DEPARTMENT = 'department', 'Departamentos Docentes'
        CAREER = 'career', 'Dirección de Carrera'
        BEDELIA = 'bedelia', 'Bedelia'
        SYSTEMS = 'systems', 'Área de Coordinación de Sistemas Académicos'

    name = models.CharField(max_length=200, verbose_name="Nombre")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(verbose_name="Fecha de fin")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.STUDENT,
        verbose_name="Categoría",
    )
    year = models.IntegerField(verbose_name="Año")
    is_deadline = models.BooleanField(default=False, verbose_name="Es vencimiento")

    class Meta:
        verbose_name = "Evento del Calendario Académico"
        verbose_name_plural = "Eventos del Calendario Académico"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.year} · {self.name} ({self.start_date} – {self.end_date})"
