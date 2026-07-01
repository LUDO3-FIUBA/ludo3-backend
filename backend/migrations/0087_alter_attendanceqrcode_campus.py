# Generated for adding Ciudad Universitaria campus choice

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0086_news_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendanceqrcode',
            name='campus',
            field=models.CharField(blank=True, choices=[('las_heras', 'Las Heras'), ('paseo_colon', 'Paseo Colón'), ('ciudad_universitaria', 'Ciudad Universitaria')], max_length=20, null=True, verbose_name='Sede'),
        ),
    ]
