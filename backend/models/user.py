from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from ..validators import validate_dni


class CustomUserManager(UserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        from .student import Student
        from .teacher import Teacher
        email = self.normalize_email(email)

        image = extra_fields.pop("image", None)
        face_encodings = extra_fields.pop("face_encodings", None)
        padron = extra_fields.pop("padron", None)

        user = self.model(email=email, **extra_fields)

        if extra_fields.get('is_student', False):
            # Estudiantes tienen contraseña obligatoria
            if not password:
                raise ValidationError('Password is required for students')
            user.set_password(password)
            user.save(using=self._db)
            Student(user=user, image=image, face_encodings=face_encodings, padron=padron).save()
        elif extra_fields.get('is_teacher', False):
            user.set_unusable_password()
            user.save(using=self._db)
            Teacher(user=user, face_encodings=face_encodings).save()
        elif extra_fields.get('is_staff', False):
            user.set_password(password)
            user.save(using=self._db)
        else:
            raise ValidationError('Either is_student, is_teacher or is_staff is needed')
        
        return user

    def create_superuser(self, email, password, username=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_student', False)
        extra_fields.setdefault('is_teacher', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    is_student = models.BooleanField(default=False, verbose_name="Es estudiante?")
    is_teacher = models.BooleanField(default=False, verbose_name="Es docente?")
    first_name = models.CharField(max_length=50, blank=True, verbose_name="Nombre")
    last_name = models.CharField(max_length=50, blank=True, verbose_name="Apellido")
    username = models.CharField(max_length=30, unique=False, blank=True, default='')
    dni = models.CharField(validators=[validate_dni], max_length=9, unique=True, blank=False, verbose_name="DNI")


    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Creado en")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Última actualización")

    objects = CustomUserManager()

    USERNAME_FIELD = 'dni'
    REQUIRED_FIELDS = ['email', 'is_student', 'is_teacher']

    def __str__(self):
        return f"{self.dni}, {self.first_name} {self.last_name}"

    def file(self):
        return self.student.padron if self.is_student else self.teacher.legajo

