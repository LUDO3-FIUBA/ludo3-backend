from django.db import migrations

DOCUMENT_FORM_NAMES = [
    'Nota al decano',
    'Certificado de alumno regular',
    'Certificado de trámite en curso',
    'Constancia de examen',
    'Mesa Especial',
    'Pedido de Prórroga de asignatura vencida',
    'Pase de carrera en FIUBA',
    'Simultaneidad en FIUBA',
    'Pase/Simultaneidad en UBA',
    'Excepción de correlatividad',
    'Reconocimiento de créditos',
    'Readmisión como alumno regular',
    'Resolución 168',
]

DIGITAL_FORM_NAMES = [
    'Solicitud cuenta de correo FI.UBA.AR',
    'Solicitud de información de intercambios académicos',
]

# Groups that were auto-created by migration 0078 from FormProcedureType rows
# seeded in migration 0061. The FormProcedureType table was dropped in 0079;
# these groups are now empty stubs with no members and no forms.
LEGACY_GROUP_NAMES = ['Administrativo', 'Exámenes', 'Carrera', 'Cursada']


def delete_seeded_forms_and_legacy_groups(apps, schema_editor):
    Form = apps.get_model('backend', 'Form')
    FormOwnershipGroup = apps.get_model('backend', 'FormOwnershipGroup')

    all_seeded_names = DOCUMENT_FORM_NAMES + DIGITAL_FORM_NAMES
    Form.objects.filter(form_name__in=all_seeded_names).delete()

    FormOwnershipGroup.objects.filter(
        name__in=LEGACY_GROUP_NAMES,
        forms__isnull=True,
    ).delete()


def reverse_delete(apps, schema_editor):
    # Intentionally irreversible: re-seeding belongs to the original migrations.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0079_remove_form_procedure'),
    ]

    operations = [
        migrations.RunPython(delete_seeded_forms_and_legacy_groups, reverse_delete),
    ]
