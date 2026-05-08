from django.db import models
from django.utils import timezone

from .semester import Semester
from .student import Student
from .attendance_qr_code import AttendanceQRCode


class Attendance(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='attendances', verbose_name="Semestre")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name="Estudiante")
    qr_code = models.ForeignKey(AttendanceQRCode, on_delete=models.CASCADE, related_name='attendances', verbose_name="Codigo QR escaneado")
    submitted_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Fecha de escaneo")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Latitud")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Longitud")
    location_valid = models.BooleanField(null=True, blank=True, verbose_name="Ubicacion valida")

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"

    def __str__(self):
        return f"{self.semester} - {self.student} - {self.submitted_at} - {self.qr_code}"
