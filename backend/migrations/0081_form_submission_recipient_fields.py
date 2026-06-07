from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0080_delete_seeded_forms_and_legacy_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='formsubmission',
            name='recipient_entity_type',
            field=models.CharField(
                blank=True,
                choices=[('department', 'Departamento'), ('secretary', 'Secretaría')],
                max_length=20,
                null=True,
                verbose_name='Tipo de destinatario',
            ),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='recipient_entity_id',
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name='ID del destinatario',
            ),
        ),
    ]
