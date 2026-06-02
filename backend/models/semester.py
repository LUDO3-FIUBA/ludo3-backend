from django.core.exceptions import ValidationError
from django.db import models
import math

from .commission import Commission
from .student import Student


class Semester(models.Model):
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, related_name='semesters', verbose_name="Semestres")

    class YearMoment(models.TextChoices):
        FIRST_SEMESTER = 'FS', 'First Semester'
        SECOND_SEMESTER = 'SS', 'Second Semester'
        INTENSIVE_WINTER = 'IW', 'Intensive Winter'
        INTENSIVE_SUMMER = 'IS', 'Intensive Summer'

    year_moment = models.CharField(
      max_length=2,
      choices=[(moment, moment.value) for moment in YearMoment],  # Choices is a list of Tuple
      default=YearMoment.FIRST_SEMESTER,
      verbose_name="Momento del año"
    )
    start_date = models.DateTimeField(db_index=True, verbose_name="Fecha de inicio")
    students =  models.ManyToManyField(Student, through='CommissionInscription', verbose_name="Alumnos Inscriptos")
    classes_amount = models.IntegerField(default=18, db_index=True, null=True, blank=True, verbose_name="Cantidad de Clases")
    minimum_attendance = models.FloatField(default=0.0, db_index=True, null=True, blank=True, verbose_name="Porcentage Minimo de Asistencias")
    calendar_source_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL del calendario de cátedra")

    # REQUIRED_FIELDS = ['date']

    # ALLOWED_FILTERS = {
    #     "year": "date__year",
    #     "grade_gte": "finalexam__grade__gte",
    #     "student": "finalexam__student"
    # }

    class Meta:
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"

    def __str__(self):
        return f"{self.commission} - {self.start_date.year} {self.year_moment}"

    def semester_evaluations_ordered(self):
        evaluations = self.evaluations
        if hasattr(evaluations, "all"):
            evaluations = evaluations.all()
        return sorted(list(evaluations), key=lambda evaluation: evaluation.end_date)

    def evaluation_chains(self):
        chains = []

        for evaluation in self.semester_evaluations_ordered():
            if not evaluation.is_graded or evaluation.parent_evaluation is not None:
                continue

            chain = [evaluation]
            current_evaluation = evaluation

            while True:
                make_up_evaluation = getattr(current_evaluation, "make_up_evaluation", None)
                if make_up_evaluation is None:
                    break

                chain.append(make_up_evaluation)
                current_evaluation = make_up_evaluation

            chains.append(chain)

        return chains

    def has_attendance_requirement(self):
        return self.classes_amount is not None and self.minimum_attendance is not None and self.minimum_attendance > 0

    def max_absences(self):
        required_attendances = math.ceil(self.classes_amount * self.minimum_attendance)
        return self.classes_amount - required_attendances

    def clean(self):
        errors = {}
        
        if self.classes_amount is not None and self.classes_amount <= 0:
            errors['classes_amount'] = 'classes_amount must be greater than 0'
        
        if self.minimum_attendance is not None:
            if self.minimum_attendance < 0 or self.minimum_attendance > 1:
                errors['minimum_attendance'] = 'minimum_attendance must be between 0 and 1'
        
        if errors:
            raise ValidationError(errors)