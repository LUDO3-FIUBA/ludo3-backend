from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0043_notification_channels_and_urgency'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE backend_notification "
                        "ADD COLUMN IF NOT EXISTS image varchar(100) NULL;"
                    ),
                    reverse_sql="ALTER TABLE backend_notification DROP COLUMN IF EXISTS image;",
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='notification',
                    name='image',
                    field=models.ImageField(
                        blank=True,
                        null=True,
                        upload_to='notifications/',
                        verbose_name='Imagen',
                    ),
                ),
            ],
        ),
    ]
