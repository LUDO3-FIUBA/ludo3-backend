from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0058_news'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='department',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='admins',
                to='backend.department',
                verbose_name='Departamento',
            ),
        ),
        migrations.AddField(
            model_name='commission',
            name='department',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='commissions',
                to='backend.department',
                verbose_name='Departamento',
            ),
        ),
    ]
