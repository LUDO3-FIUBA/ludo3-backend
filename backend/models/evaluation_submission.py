from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from backend.services.file_validator_service import FileValidatorService
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
    
    submission_text = models.TextField(null=True, blank=True)
    submission_status = models.CharField(max_length=12, choices=SubmissionStatus.choices, null=True, blank=True, db_index=True, verbose_name="Estado de la entrega")
    submission_file = models.FileField(upload_to='submissions/', null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Creado en")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Última actualización")

    def clean(self):
        # No permitir nota numérica y estado aprobado/desaprobado al mismo tiempo
        if self.grade is not None and self.submission_status is not None:
            raise ValidationError("Usar calificación numérica o estado APROBADO/DESAPROBADO, no ambas")

        if not self.evaluation.is_gradeable and self.grade is not None:
            raise ValidationError({"grade": ["Esta evaluación usa estado APROBADO/DESAPROBADO."]})

        if self.evaluation.is_gradeable and self.submission_status is not None:
            raise ValidationError({"submission_status": ["Esta evaluación usa calificación numérica."]})

        if self.submission_file:
            self._validate_submission_file()

    def _validate_submission_file(self):
        uploaded_file = self.submission_file
        file_obj = getattr(uploaded_file, 'file', uploaded_file)

        try:
            is_pdf = FileValidatorService.validate_pdf(file_obj)
            is_image = FileValidatorService.validate_image(file_obj)
            
            if not (is_pdf or is_image):
                raise ValidationError({
                    'submission_file': ['El archivo debe ser un PDF o una imagen válida (jpg, jpeg, png, webp).']
                })
        except ValidationError:
            raise

    def is_passed(self):
        if self.evaluation is None:
            return False

        if self.evaluation.is_gradeable:
            if self.grade is None or self.evaluation.passing_grade is None:
                return False

            return self.grade >= self.evaluation.passing_grade

        return self.submission_status == self.SubmissionStatus.APROBADO

    def __str__(self):
        return f"{self.student} - {self.evaluation} - {self.grade}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['evaluation', 'student'], name='one_submission_per_student')
        ]

        verbose_name = "Entrega de Evaluacion"
        verbose_name_plural = "Entregas de Evaluacion"
