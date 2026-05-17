from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0072_merge_20260515_2035'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='is_bedelia',
            field=models.BooleanField(default=False, verbose_name='Es bedelía?'),
        ),
    ]
