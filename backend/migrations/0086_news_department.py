from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0085_notification_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='department',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='news',
                to='backend.department',
                verbose_name='Departamento',
            ),
        ),
    ]
