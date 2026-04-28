from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0056_merge_20260420_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='semester',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='notifications',
                to='backend.semester',
                verbose_name='Cuatrimestre',
            ),
        ),
    ]
