from django.db import migrations, models


def migrate_location_to_qr_location(apps, schema_editor):
    AttendanceQRCode = apps.get_model('backend', 'AttendanceQRCode')
    AttendanceQRCode.objects.filter(mode='location').update(mode='qr_location')


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0058_auto_20260508_2255'),
    ]

    operations = [
        # Ampliar columna e incluir los tres valores temporalmente para que la data migration no falle
        migrations.AlterField(
            model_name='attendanceqrcode',
            name='mode',
            field=models.CharField(
                choices=[('qr', 'QR'), ('location', 'Ubicación'), ('qr_location', 'QR + Ubicación')],
                default='qr',
                max_length=11,
                verbose_name='Modo de asistencia',
            ),
        ),
        # Migrar datos: location -> qr_location
        migrations.RunPython(
            migrate_location_to_qr_location,
            reverse_code=migrations.RunPython.noop,
        ),
        # Quitar 'location' de los choices
        migrations.AlterField(
            model_name='attendanceqrcode',
            name='mode',
            field=models.CharField(
                choices=[('qr', 'QR'), ('qr_location', 'QR + Ubicación')],
                default='qr',
                max_length=11,
                verbose_name='Modo de asistencia',
            ),
        ),
    ]
