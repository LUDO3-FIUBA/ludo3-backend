from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from .teacher import Teacher


class TeacherProfile(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    university = models.CharField(max_length=255, verbose_name="Universidad")
    degree = models.CharField(max_length=255, verbose_name="Título / Carrera")
    bio = models.TextField(blank=True, verbose_name="Descripción personal")
    current_position = models.CharField(max_length=255, verbose_name="Cargo actual")
    years_of_experience = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(70)])
    certifications = models.TextField(blank=True)
    linkedin_url = models.URLField(max_length=255, blank=True, verbose_name="LinkedIn")

    class Meta:
        verbose_name = 'Perfil Profesional Docente'
        verbose_name_plural = 'Perfiles Profesionales Docentes'


class WorkExperience(models.Model):
    profile = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='work_experience')
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    start_year = models.PositiveIntegerField(validators=[MinValueValidator(1950), MaxValueValidator(2100)])
    end_year = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1950), MaxValueValidator(2100)])
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_year']
