from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0084_merge_20260603_0101'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='department',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='notifications',
                to='backend.department',
                verbose_name='Departamento',
            ),
        ),
    ]
