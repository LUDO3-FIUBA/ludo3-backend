import uuid

from django.db import models
from django.utils import timezone

from backend.services.siu_service import SiuService
from backend.utils import memoized

from .commission import Commission
from .teacher import Teacher


class Final(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        REJECTED = 'RJ', 'Rejected'
        OPEN = 'OP', 'Open'
        PENDING_ACT = 'PA', 'Pending Act'
        ACT_SENT = 'AS', 'Act Sent'

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='finals', verbose_name="Docente")
    commissions = models.ManyToManyField(Commission, related_name='finals', blank=True, verbose_name="Comisiones")
    date = models.DateTimeField(db_index=True, null=False, editable=False, verbose_name="Fecha")
    subject_siu_id = models.IntegerField(db_index=True, default=0, null=False, editable=False, verbose_name="SIU ID de Materia")
    subject_name = models.CharField(max_length=100, db_index=True, null=False, editable=False, verbose_name="Nombre de Materia")
    qrid = models.UUIDField(default=uuid.uuid4, editable=False)
    siu_id = models.IntegerField(db_index=True, null=True, editable=True)
    status = models.CharField(
      max_length=2,
      choices=[(tag, tag.value) for tag in Status],  # Choices is a list of Tuple
      default=Status.DRAFT,
      verbose_name="Estado"
    )
    act = models.CharField(max_length=10, db_index=True, null=True, verbose_name="Nro de Acta")

    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Creado en")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Última Actualización")

    REQUIRED_FIELDS = ['date']

    ALLOWED_FILTERS = {
        "year": "date__year",
        "grade_gte": "finalexam__grade__gte",
        "student": "finalexam__student"
    }

    class Meta:
        verbose_name = "Final"
        verbose_name_plural = "Finales"

    @memoized
    def subject(self):
        return SiuService().get_subject(self.subject_siu_id)

    def __str__(self):
        return f"{self.siu_id} - {self.subject_name} - {self.teacher} - {self.date.date()}"
