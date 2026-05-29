from django.db import migrations, models


def backfill_final_commissions(apps, schema_editor):
    Final = apps.get_model('backend', 'Final')
    Commission = apps.get_model('backend', 'Commission')

    for final in Final.objects.all():
        matching = Commission.objects.filter(
            chief_teacher=final.teacher,
            subject_siu_id=final.subject_siu_id,
        )
        if matching.exists():
            final.commissions.set(matching)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0075_auto_20260520_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='final',
            name='commissions',
            field=models.ManyToManyField(blank=True, related_name='finals', to='backend.Commission', verbose_name='Comisiones'),
        ),
        migrations.RunPython(backfill_final_commissions, noop_reverse),
    ]
