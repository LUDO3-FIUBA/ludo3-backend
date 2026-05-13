from datetime import date, timedelta

from django.core.management import BaseCommand

from backend.models import AcademicCalendarEvent, CalendarEventReminder, Notification, UserNotification
from backend.models.user import User


class Command(BaseCommand):
    help = "Envía notificaciones de recordatorio para eventos del calendario académico con is_deadline=True"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-before',
            type=str,
            default='7,3,1',
            help='Lista de días de anticipación separados por coma (default: 7,3,1)',
        )

    def handle(self, *args, **options):
        days_list = [int(d.strip()) for d in options['days_before'].split(',')]
        today = date.today()

        students = User.objects.filter(is_student=True)
        if not students.exists():
            self.stdout.write("No hay alumnos en el sistema.")
            return

        total_sent = 0

        for days in days_list:
            target_date = today + timedelta(days=days)
            events = AcademicCalendarEvent.objects.filter(
                is_deadline=True,
                start_date=target_date,
            )

            for event in events:
                already_sent = CalendarEventReminder.objects.filter(
                    event=event,
                    days_before=days,
                ).exists()

                if already_sent:
                    self.stdout.write(f"Ya enviado: '{event.name}' ({days}d antes) — saltando")
                    continue

                if days == 1:
                    days_label = "mañana"
                elif days == 0:
                    days_label = "hoy"
                else:
                    days_label = f"en {days} días"

                notification = Notification.objects.create(
                    title=f"Recordatorio: {event.name}",
                    message=f"El evento '{event.name}' vence {days_label} ({event.start_date}).",
                    sender=None,
                    is_urgent=(days <= 1),
                    send_push=False,
                    send_email=False,
                )

                UserNotification.objects.bulk_create([
                    UserNotification(notification=notification, user=student)
                    for student in students
                ])

                CalendarEventReminder.objects.create(
                    event=event,
                    days_before=days,
                    notification=notification,
                )

                total_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Enviado: '{event.name}' a {students.count()} alumnos ({days}d antes)"
                    )
                )

        if total_sent == 0:
            self.stdout.write("Ningún recordatorio para enviar hoy.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Listo. {total_sent} recordatorio(s) enviado(s)."))
