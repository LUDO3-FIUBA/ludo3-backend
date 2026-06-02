from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0075_auto_20260520_0602'),
    ]

    operations = [
        # 1. Create the Secretary model.
        migrations.CreateModel(
            name='Secretary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre')),
                ('location', models.CharField(blank=True, default='', max_length=300, verbose_name='Ubicación')),
                ('schedule', models.TextField(blank=True, default='', verbose_name='Horario de atención')),
                ('contact_info', models.TextField(blank=True, default='', verbose_name='Información de contacto')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('parent_secretary', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='subsecretaries',
                    to='backend.secretary',
                    verbose_name='Secretaría padre',
                )),
            ],
            options={
                'verbose_name': 'Secretaría',
                'verbose_name_plural': 'Secretarías',
                'ordering': ['name'],
            },
        ),

        # 2. Add FK from Staff to Secretary.
        migrations.AddField(
            model_name='staff',
            name='secretary',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='admins',
                to='backend.secretary',
                verbose_name='Secretaría',
            ),
        ),

        # 3. Database-level constraint: department and secretary cannot both be set.
        migrations.AddConstraint(
            model_name='staff',
            constraint=models.CheckConstraint(
                check=(
                    models.Q(department__isnull=True) | models.Q(secretary__isnull=True)
                ),
                name='staff_department_or_secretary_not_both',
            ),
        ),
    ]
