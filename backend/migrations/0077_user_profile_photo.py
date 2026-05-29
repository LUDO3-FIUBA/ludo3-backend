from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0076_final_commissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_photo',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Foto de perfil'),
        ),
    ]
