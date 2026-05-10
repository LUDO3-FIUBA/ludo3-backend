from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0063_seed_digital_forms'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='github_url',
            field=models.URLField(blank=True, max_length=255, verbose_name='GitHub'),
        ),
    ]
