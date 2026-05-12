import uuid

from django.db import models
from django.utils import timezone

from backend.services.siu_service import SiuService
from backend.utils import memoized

from .department import Department
from .teacher import Teacher


class Commission(models.Model):
    chief_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='commissions', verbose_name="Docente")
    subject_siu_id = models.IntegerField(db_index=True, default=0, null=False, verbose_name="SIU ID de Materia")
    subject_name = models.CharField(max_length=100, db_index=True, null=False, verbose_name="Nombre de Materia")
    siu_id = models.IntegerField(db_index=True, null=False, editable=False)
    chief_teacher_grader_weight = models.FloatField(default=5.0, verbose_name="Peso al asignar correctores")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commissions',
        verbose_name="Departamento",
    )

    teachers =  models.ManyToManyField(Teacher, through='TeacherRole', verbose_name="Cuerpo Docente")

    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Creado en")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Última Actualización")

    # REQUIRED_FIELDS = ['date']

    # ALLOWED_FILTERS = {
    #     "year": "date__year",
    #     "grade_gte": "finalexam__grade__gte",
    #     "student": "finalexam__student"
    # }

    class Meta:
        verbose_name = "Comisión"
        verbose_name_plural = "Comisiones"

    @memoized
    def subject(self):
        return SiuService().get_subject(self.subject_siu_id)

    def __str__(self):
        return f"{self.siu_id} - {self.subject_name} - {self.chief_teacher}"