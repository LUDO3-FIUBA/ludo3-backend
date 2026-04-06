from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0043_semesterschedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicCalendarEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre')),
                ('start_date', models.DateField(verbose_name='Fecha de inicio')),
                ('end_date', models.DateField(verbose_name='Fecha de fin')),
                ('category', models.CharField(
                    choices=[
                        ('student', 'Estudiantes'),
                        ('teacher', 'Docentes'),
                        ('department', 'Departamentos Docentes'),
                        ('career', 'Dirección de Carrera'),
                        ('bedelia', 'Bedelia'),
                        ('systems', 'Área de Coordinación de Sistemas Académicos'),
                    ],
                    default='student',
                    max_length=20,
                    verbose_name='Categoría',
                )),
                ('year', models.IntegerField(verbose_name='Año')),
            ],
            options={
                'verbose_name': 'Evento del Calendario Académico',
                'verbose_name_plural': 'Eventos del Calendario Académico',
                'ordering': ['start_date'],
            },
        ),
    ]
