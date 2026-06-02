from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0082_merge_20260527_0224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formdocumentsource',
            name='form_document_source',
            field=models.CharField(max_length=500, verbose_name='Documento (clave relativa o URL)'),
        ),
    ]
