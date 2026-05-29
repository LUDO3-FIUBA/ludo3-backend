from django.db import models

from .career import Career
from .student import Student


class StudentCareer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_careers')
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='student_careers')
    plan = models.CharField(max_length=50, blank=True, default='')
    enrollment_date = models.DateField(null=True, blank=True)
    graduation_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'career')
        verbose_name = 'Carrera de Alumno'
        verbose_name_plural = 'Carreras de Alumnos'
