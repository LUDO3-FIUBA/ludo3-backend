from django.db import models

from .semester import Semester
from .commission import Commission


class Evaluation(models.Model):
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, related_name='evaluations', verbose_name="Comisión", default=1)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='evaluations', verbose_name="Evaluaciones")
    evaluation_name = models.CharField(max_length=100, db_index=True, editable=False, verbose_name="Nombre de Evaluacion")
    is_graded = models.BooleanField(default=True)
    passing_grade = models.IntegerField(db_index=True, null=True, blank=True, verbose_name="Nota de Aprobacion")
    requires_qr = models.BooleanField(default=False, verbose_name="Requiere escanear QR")
    requires_identity = models.BooleanField(default=False, verbose_name="Requiere verificación de identidad")

    parent_evaluation = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Evaluacion a recuperar", related_name='make_up_evaluation')
    """Apunta a evaluacion 'padre'. Si esta definido, entonces esta Evaluation es un recuperatorio."""

    start_date = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name="Fecha de inicio")
    end_date = models.DateTimeField(db_index=True, verbose_name="Fecha de entrega")


    class Meta:
        verbose_name = "Evaluation"
        verbose_name_plural = "Evaluation"

    def __str__(self):
        return f"{self.semester} - {self.evaluation_name}"