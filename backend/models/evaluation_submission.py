from django.db import models
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from .evaluation import Evaluation
from .student import Student
from .teacher import Teacher


class EvaluationSubmission(models.Model):
    class SubmissionStatus(models.TextChoices):
        APROBADO = "APROBADO", "Aprobado"
        DESAPROBADO = "DESAPROBADO", "Desaprobado"

    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='submissions', verbose_name="Evaluacion")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions', verbose_name="Estudiante")
    grade = models.IntegerField(null=True, blank=True, db_index=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Nota")
    grader = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.CASCADE, related_name='grader', verbose_name="Grader")
    
    file = models.FileField(upload_to='evaluation_submissions/', null=True, blank=True)
    submission_text = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=SubmissionStatus.choices, null=True, blank=True, db_index=True, verbose_name="Estado de la entrega")
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Creado en")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Última actualización")

    # def clean(self):
    #     if not any([self.file, self.submission_text]):
    #         raise ValidationError("At least one submission format is required: file, URL, or text.")

    def clean(self):
        # No permitir nota numérica y estado aprobado/desaprobado al mismo tiempo
        if self.grade is not None and self.status is not None:
            raise ValidationError("Usar calificación numérica o estado APROBADO/DESAPROBADO, no ambas")

        if not self.evaluation.is_gradeable and self.grade is not None:
            raise ValidationError({"grade": ["Esta evaluación usa estado APROBADO/DESAPROBADO."]})

        if self.evaluation.is_gradeable and self.status is not None:
            raise ValidationError({"status": ["Esta evaluación usa calificación numérica."]})

    def __str__(self):
        return f"{self.student} - {self.evaluation} - {self.grade}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['evaluation', 'student'], name='one_submission_per_student')
        ]

        verbose_name = "Entrega de Evaluacion"
        verbose_name_plural = "Entregas de Evaluacion"
