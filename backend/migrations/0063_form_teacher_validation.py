from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0062_form_submission_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='requires_teacher_validation',
            field=models.BooleanField(default=False, verbose_name='Requiere validación docente'),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='teacher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='form_validations',
                to='backend.teacher',
                verbose_name='Docente validador',
            ),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='teacher_status',
            field=models.CharField(
                blank=True,
                choices=[('pending', 'Pendiente'), ('approved', 'Aprobado'), ('denied', 'Rechazado')],
                max_length=20,
                null=True,
                verbose_name='Estado de validación docente',
            ),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='teacher_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Comentario del docente'),
        ),
    ]
