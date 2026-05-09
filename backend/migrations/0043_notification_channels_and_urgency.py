from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0042_notification_usernotification'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE backend_notification "
                        "ADD COLUMN IF NOT EXISTS is_urgent boolean DEFAULT false NOT NULL;"
                    ),
                    reverse_sql="ALTER TABLE backend_notification DROP COLUMN IF EXISTS is_urgent;",
                ),
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE backend_notification "
                        "ADD COLUMN IF NOT EXISTS send_push boolean DEFAULT false NOT NULL;"
                    ),
                    reverse_sql="ALTER TABLE backend_notification DROP COLUMN IF EXISTS send_push;",
                ),
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE backend_notification "
                        "ADD COLUMN IF NOT EXISTS send_email boolean DEFAULT false NOT NULL;"
                    ),
                    reverse_sql="ALTER TABLE backend_notification DROP COLUMN IF EXISTS send_email;",
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='notification',
                    name='is_urgent',
                    field=models.BooleanField(default=False, verbose_name='Urgente'),
                ),
                migrations.AddField(
                    model_name='notification',
                    name='send_push',
                    field=models.BooleanField(default=False, verbose_name='Enviar push'),
                ),
                migrations.AddField(
                    model_name='notification',
                    name='send_email',
                    field=models.BooleanField(default=False, verbose_name='Enviar email'),
                ),
            ],
        ),
    ]
