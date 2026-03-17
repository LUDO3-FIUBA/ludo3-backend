from django.db import models
from django.utils import timezone

from django.core.exceptions import ValidationError

from .evaluation import Evaluation
from .student import Student
from .teacher import Teacher


class EvaluationSubmission(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='submissions', verbose_name="Evaluacion")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions', verbose_name="Estudiante")
    grade = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="Nota")
    grader = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.CASCADE, related_name='grader', verbose_name="Grader")
    
    file = models.FileField(upload_to='evaluation_submissions/', null=True, blank=True)
    submission_text = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Creado en")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Última actualización")

    # def clean(self):
    #     if not any([self.file, self.submission_text]):
    #         raise ValidationError("At least one submission format is required: file, URL, or text.")

    def __str__(self):
        return f"{self.student} - {self.evaluation} - {self.grade}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['evaluation', 'student'], name='one_submission_per_student')
        ]

        verbose_name = "Entrega de Evaluacion"
        verbose_name_plural = "Entregas de Evaluacion"
