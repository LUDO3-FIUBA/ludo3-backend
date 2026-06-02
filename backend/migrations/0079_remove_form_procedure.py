from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0078_migrate_procedure_types_to_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='form',
            name='form_procedure',
        ),
        migrations.AlterField(
            model_name='form',
            name='ownership_group',
            field=models.ForeignKey(
                null=False,
                blank=False,
                on_delete=models.deletion.PROTECT,
                related_name='forms',
                to='backend.formownershipgroup',
                verbose_name='Grupo de propiedad',
            ),
        ),
        migrations.DeleteModel(
            name='FormProcedureType',
        ),
    ]
