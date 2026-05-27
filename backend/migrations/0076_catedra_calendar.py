from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0075_auto_20260520_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='semester',
            name='calendar_source_url',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='URL del calendario de cátedra'),
        ),
        migrations.CreateModel(
            name='CatedraCalendarEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Fecha')),
                ('class_number', models.IntegerField(blank=True, null=True, verbose_name='Número de clase')),
                ('topic', models.CharField(max_length=500, verbose_name='Tema')),
                ('entry_type', models.CharField(
                    choices=[
                        ('class', 'Clase'),
                        ('tp_delivery', 'Entrega TP'),
                        ('exam', 'Parcial'),
                        ('holiday', 'Feriado'),
                        ('other', 'Otro'),
                    ],
                    default='class',
                    max_length=20,
                    verbose_name='Tipo',
                )),
                ('links', models.JSONField(blank=True, default=list, verbose_name='Links')),
                ('notes', models.TextField(blank=True, default='', verbose_name='Notas')),
                ('semester', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='catedra_calendar',
                    to='backend.semester',
                    verbose_name='Semestre',
                )),
            ],
            options={
                'verbose_name': 'Entrada del Calendario de Cátedra',
                'verbose_name_plural': 'Entradas del Calendario de Cátedra',
                'ordering': ['date', 'class_number'],
            },
        ),
    ]
