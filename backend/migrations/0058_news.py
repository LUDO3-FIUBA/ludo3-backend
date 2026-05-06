from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0057_notification_semester'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(blank=True, default='', verbose_name='Descripción')),
                ('picture_url', models.URLField(blank=True, default='', max_length=500, verbose_name='Imagen')),
                ('tag', models.CharField(choices=[('deportes', 'Deportes'), ('institucional', 'Institucional'), ('laboratorio', 'Laboratorio')], max_length=50, verbose_name='Categoría')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posted_news', to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
            ],
            options={
                'verbose_name': 'Novedad',
                'verbose_name_plural': 'Novedades',
                'ordering': ['-created_at'],
            },
        ),
    ]
