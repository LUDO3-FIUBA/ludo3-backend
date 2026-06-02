from django.db import models
from django.utils import timezone

from .academic_calendar_event import AcademicCalendarEvent
from .semester import Semester
from .user import User


class Notification(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name="Remitente"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Creado en")
    is_urgent = models.BooleanField(default=False, verbose_name="Urgente")
    send_push = models.BooleanField(default=False, verbose_name="Enviar push")
    send_email = models.BooleanField(default=False, verbose_name="Enviar email")
    image = models.ImageField(upload_to='notifications/', null=True, blank=True, verbose_name="Imagen")
    action_url = models.CharField(max_length=200, null=True, blank=True, verbose_name="URL de acción")
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name="Cuatrimestre"
    )

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return self.title


class UserNotification(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='user_notifications',
        verbose_name="Notificación"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Usuario"
    )
    is_read = models.BooleanField(default=False, verbose_name="Leída")

    class Meta:
        verbose_name = "Notificación de usuario"
        verbose_name_plural = "Notificaciones de usuario"
        unique_together = ('notification', 'user')


class CalendarEventReminder(models.Model):
    event = models.ForeignKey(
        AcademicCalendarEvent,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name="Evento",
    )
    days_before = models.IntegerField(verbose_name="Días de anticipación")
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='calendar_reminder',
        verbose_name="Notificación generada",
    )
    sent_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Enviado el")

    class Meta:
        verbose_name = "Recordatorio de evento"
        verbose_name_plural = "Recordatorios de eventos"
        unique_together = ('event', 'days_before')
