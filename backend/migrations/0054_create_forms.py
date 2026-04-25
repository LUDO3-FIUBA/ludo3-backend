import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def seed_form_types(apps, schema_editor):
    FormProcedureType = apps.get_model('backend', 'FormProcedureType')
    FormType = apps.get_model('backend', 'FormType')
    FormFieldType = apps.get_model('backend', 'FormFieldType')

    for value in ['Administrativo', 'Exámenes', 'Carrera', 'Cursada']:
        FormProcedureType.objects.create(form_procedure_value=value)

    for value in ['Digital', 'Documento']:
        FormType.objects.create(form_type_value=value)

    for value in ['texto', 'numero', 'padron', 'mail', 'options', 'catalog', 'checkbox', 'adjunto']:
        FormFieldType.objects.create(form_field_type_value=value)


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0053_merge_20260413_2247'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FormProcedureType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_procedure_value', models.CharField(max_length=100, verbose_name='Tipo de trámite')),
            ],
            options={
                'verbose_name': 'Tipo de trámite',
                'verbose_name_plural': 'Tipos de trámite',
            },
        ),
        migrations.CreateModel(
            name='FormType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_type_value', models.CharField(max_length=100, verbose_name='Tipo de formulario')),
            ],
            options={
                'verbose_name': 'Tipo de formulario',
                'verbose_name_plural': 'Tipos de formulario',
            },
        ),
        migrations.CreateModel(
            name='FormFieldType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_field_type_value', models.CharField(max_length=100, verbose_name='Tipo de campo')),
            ],
            options={
                'verbose_name': 'Tipo de campo de formulario',
                'verbose_name_plural': 'Tipos de campo de formulario',
            },
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catalog_key', models.CharField(max_length=100, unique=True, verbose_name='Clave')),
                ('catalog_name', models.CharField(max_length=200, verbose_name='Nombre')),
                ('catalog_description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name': 'Catálogo',
                'verbose_name_plural': 'Catálogos',
            },
        ),
        migrations.CreateModel(
            name='CatalogItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catalog_item_value', models.CharField(max_length=100, verbose_name='Valor')),
                ('catalog_item_label', models.CharField(max_length=200, verbose_name='Etiqueta')),
                ('catalog_item_order', models.IntegerField(blank=True, null=True, verbose_name='Orden')),
                ('catalog_item_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('catalog', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='backend.catalog',
                    verbose_name='Catálogo',
                )),
            ],
            options={
                'verbose_name': 'Item de catálogo',
                'verbose_name_plural': 'Items de catálogo',
                'ordering': ['catalog_item_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('form_description', models.CharField(max_length=300, verbose_name='Descripción')),
                ('form_information', models.TextField(blank=True, null=True, verbose_name='Información adicional')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Creado en')),
                ('form_procedure', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='forms',
                    to='backend.formproceduretype',
                    verbose_name='Tipo de trámite',
                )),
                ('form_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='forms',
                    to='backend.formtype',
                    verbose_name='Tipo de formulario',
                )),
            ],
            options={
                'verbose_name': 'Formulario',
                'verbose_name_plural': 'Formularios',
            },
        ),
        migrations.CreateModel(
            name='FormDocumentSource',
            fields=[
                ('form', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    related_name='document_source',
                    serialize=False,
                    to='backend.form',
                    verbose_name='Formulario',
                )),
                ('form_document_source', models.URLField(verbose_name='URL del documento')),
            ],
            options={
                'verbose_name': 'Fuente de documento',
                'verbose_name_plural': 'Fuentes de documento',
            },
        ),
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_field_label', models.CharField(max_length=200, verbose_name='Etiqueta')),
                ('form_field_require', models.BooleanField(default=False, verbose_name='Obligatorio')),
                ('form_field_order', models.IntegerField(verbose_name='Orden')),
                ('catalog', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='form_fields',
                    to='backend.catalog',
                    verbose_name='Catálogo',
                )),
                ('form', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='fields',
                    to='backend.form',
                    verbose_name='Formulario',
                )),
                ('form_field_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='form_fields',
                    to='backend.formfieldtype',
                    verbose_name='Tipo de campo',
                )),
            ],
            options={
                'verbose_name': 'Campo de formulario',
                'verbose_name_plural': 'Campos de formulario',
                'ordering': ['form_field_order'],
            },
        ),
        migrations.CreateModel(
            name='FormFieldOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_option_value', models.CharField(max_length=100, verbose_name='Valor')),
                ('form_option_label', models.CharField(max_length=200, verbose_name='Etiqueta')),
                ('form_field', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='options',
                    to='backend.formfield',
                    verbose_name='Campo',
                )),
            ],
            options={
                'verbose_name': 'Opción de campo',
                'verbose_name_plural': 'Opciones de campo',
            },
        ),
        migrations.CreateModel(
            name='FormSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Enviado en')),
                ('form', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='submissions',
                    to='backend.form',
                    verbose_name='Formulario',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='form_submissions',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuario',
                )),
            ],
            options={
                'verbose_name': 'Respuesta de formulario',
                'verbose_name_plural': 'Respuestas de formulario',
            },
        ),
        migrations.CreateModel(
            name='FormAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_value', models.TextField(blank=True, null=True, verbose_name='Valor de respuesta')),
                ('field', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='answers',
                    to='backend.formfield',
                    verbose_name='Campo',
                )),
                ('submission', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='answers',
                    to='backend.formsubmission',
                    verbose_name='Respuesta',
                )),
            ],
            options={
                'verbose_name': 'Respuesta de campo',
                'verbose_name_plural': 'Respuestas de campo',
            },
        ),
        migrations.RunPython(seed_form_types, migrations.RunPython.noop),
    ]
