import django.db.models.deletion
from django.db import migrations, models


STATUS_VALUES = ['sent', 'pending_approval', 'approved', 'denied']


def seed_statuses_and_backfill(apps, schema_editor):
    FormSubmissionStatus = apps.get_model('backend', 'FormSubmissionStatus')
    FormSubmission = apps.get_model('backend', 'FormSubmission')

    for value in STATUS_VALUES:
        FormSubmissionStatus.objects.get_or_create(form_submission_status_value=value)

    sent = FormSubmissionStatus.objects.get(form_submission_status_value='sent')
    FormSubmission.objects.filter(status__isnull=True).update(status=sent)


def remove_statuses(apps, schema_editor):
    FormSubmissionStatus = apps.get_model('backend', 'FormSubmissionStatus')
    FormSubmissionStatus.objects.filter(form_submission_status_value__in=STATUS_VALUES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0057_seed_digital_forms'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormSubmissionStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_submission_status_value', models.CharField(max_length=50, unique=True, verbose_name='Estado de respuesta')),
            ],
            options={
                'verbose_name': 'Estado de respuesta',
                'verbose_name_plural': 'Estados de respuesta',
            },
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='status',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='submissions',
                to='backend.formsubmissionstatus',
                verbose_name='Estado',
            ),
        ),
        migrations.RunPython(seed_statuses_and_backfill, remove_statuses),
        migrations.AlterField(
            model_name='formsubmission',
            name='status',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='submissions',
                to='backend.formsubmissionstatus',
                verbose_name='Estado',
            ),
        ),
    ]
