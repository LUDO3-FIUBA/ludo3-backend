import sys
from django.db import migrations


def migrate_procedure_types_to_groups(apps, schema_editor):
    FormProcedureType = apps.get_model('backend', 'FormProcedureType')
    FormOwnershipGroup = apps.get_model('backend', 'FormOwnershipGroup')
    Form = apps.get_model('backend', 'Form')

    type_to_group = {}
    for proc_type in FormProcedureType.objects.all():
        group, _ = FormOwnershipGroup.objects.get_or_create(
            name=proc_type.form_procedure_value,
            defaults={'name': proc_type.form_procedure_value},
        )
        type_to_group[proc_type.pk] = group

    for form in Form.objects.select_related('form_procedure').all():
        if form.form_procedure_id is not None:
            group = type_to_group.get(form.form_procedure_id)
            if group:
                form.ownership_group = group
                form.save(update_fields=['ownership_group'])

    orphan_groups = [
        g for g in FormOwnershipGroup.objects.all()
        if not g.members.filter(is_editor=True).exists()
    ]
    if orphan_groups:
        names = ', '.join(g.name for g in orphan_groups)
        print(
            f"\n[WARN] Los siguientes grupos de propiedad no tienen editores: {names}. "
            "Asignar editores desde el panel de superadmin (Etapa 3).",
            file=sys.stderr,
        )


def reverse_migrate(apps, schema_editor):
    FormOwnershipGroup = apps.get_model('backend', 'FormOwnershipGroup')
    Form = apps.get_model('backend', 'Form')
    for form in Form.objects.all():
        form.ownership_group = None
        form.save(update_fields=['ownership_group'])
    FormOwnershipGroup.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0077_form_ownership_group'),
    ]

    operations = [
        migrations.RunPython(migrate_procedure_types_to_groups, reverse_migrate),
    ]
