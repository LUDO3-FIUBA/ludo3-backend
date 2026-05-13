from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0057_notification_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='academiccalendarevent',
            name='is_deadline',
            field=models.BooleanField(default=False, verbose_name='Es vencimiento'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='sender',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='sent_notifications',
                to='backend.user',
                verbose_name='Remitente',
            ),
        ),
        migrations.CreateModel(
            name='CalendarEventReminder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days_before', models.IntegerField(verbose_name='Días de anticipación')),
                ('sent_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Enviado el')),
                ('event', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reminders',
                    to='backend.academiccalendarevent',
                    verbose_name='Evento',
                )),
                ('notification', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='calendar_reminder',
                    to='backend.notification',
                    verbose_name='Notificación generada',
                )),
            ],
            options={
                'verbose_name': 'Recordatorio de evento',
                'verbose_name_plural': 'Recordatorios de eventos',
            },
        ),
        migrations.AlterUniqueTogether(
            name='calendareventreminder',
            unique_together={('event', 'days_before')},
        ),
    ]
