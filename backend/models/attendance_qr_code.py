import uuid
from django.db import models
from django.utils import timezone

from .semester import Semester
from .teacher import Teacher


def three_hours_from_now():
    return timezone.now() + timezone.timedelta(hours=3)


MODE_QR = 'qr'
MODE_LOCATION = 'location'
MODE_CHOICES = [(MODE_QR, 'QR'), (MODE_LOCATION, 'Ubicación')]

CAMPUS_LAS_HERAS = 'las_heras'
CAMPUS_PASEO_COLON = 'paseo_colon'
CAMPUS_CHOICES = [(CAMPUS_LAS_HERAS, 'Las Heras'), (CAMPUS_PASEO_COLON, 'Paseo Colón')]


class AttendanceQRCode(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='attendance_qrs', verbose_name="Semestre")
    owner_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances_qrs', verbose_name="Docente que creo el QR")
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Fecha de creacion")
    expires_at = models.DateTimeField(default=three_hours_from_now, verbose_name="Fecha de expiracion")
    qrid = models.UUIDField(default=uuid.uuid4, editable=False)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default=MODE_QR, verbose_name="Modo de asistencia")
    campus = models.CharField(max_length=20, choices=CAMPUS_CHOICES, null=True, blank=True, verbose_name="Sede")

    class Meta:
        verbose_name = "QR de Asistencias"
        verbose_name_plural = "QRs de Asistencias"

    def __str__(self):
        return f"{self.semester} - {self.owner_teacher} - {self.created_at} - {self.qrid}"
