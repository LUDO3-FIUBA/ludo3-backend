from django.db import migrations


DIGITAL_FORMS = [
    {
        'form_name': 'Solicitud cuenta de correo FI.UBA.AR',
        'form_description': 'Solicitud de mail institucional FIUBA',
        'form_information': (
            'El alta tiene un tiempo estimado maximo de 72hs habiles. Una vez generada la cuenta se le enviara '
            'desde el remitente de Mesa de Ayuda o Google Workspace un correo con los datos de acceso. '
            'Verificar siempre la carpeta de spam o correos no deseados en caso de que hayan transcurrido mas '
            'de las 72hs habiles.\n\n'
            'NOTA: En el caso de los alumnos de grado, es condicion necesaria tener numero de legajo asignado para '
            'obtener un correo Fiuba.\n\n'
            'Informacion importante:\n'
            '1- Los campos nombre y apellido deben ser completados de forma completa.\n'
            '2- NO completar el formulario mas de una vez. El completar el formulario varias veces solo perjudica '
            'el procesamiento de datos y hace que los tiempos de creacion sean aun mayores.\n'
            '3- En caso de ser alumno de posgrado, una vez completado el formulario deberan enviar a ayuda@fi.uba.ar '
            'la constancia de que se encuentra realizando un Posgrado en la Facultad. En caso de no enviar la '
            'informacion no se procedera con lo solicitado.\n'
            '4- En caso de ser alumno del CBC los correos electronicos FIUBA son otorgados solamente a los alumnos '
            'del CBC que esten cursando una materia en la Facultad (no incluye materias del CBC) o bien para '
            'aquellos que lo necesiten para algun tramite administrativo. En el primer caso le pedimos que una vez '
            'completado el formulario envie a ayuda@fi.uba.ar el nombre de la materia, carrera, nombre, apellido y '
            'correo electronico del docente a cargo de la materia. En el segundo caso, le solicitamos que una vez '
            'completado el formulario envie a ayuda@fi.uba.ar el tipo de tramite administrativo a realizar. En caso '
            'de no enviar la informacion no se procedera con lo solicitado.'
        ),
        'form_procedure_value': 'Administrativo',
        'fields': [
            {
                'label': 'Correo',
                'field_type': 'mail',
                'required': True,
            },
            {
                'label': 'Nombre',
                'field_type': 'texto',
                'required': True,
            },
            {
                'label': 'Apellido',
                'field_type': 'texto',
                'required': True,
            },
            {
                'label': 'DNI',
                'field_type': 'numero',
                'required': True,
            },
            {
                'label': 'Rol en la comunidad FIUBA',
                'field_type': 'catalog',
                'required': True,
                'catalog_key': 'rol_en_comunidad',
            },
            {
                'label': 'Legajo o Padron',
                'field_type': 'padron',
                'required': True,
            },
            {
                'label': 'Email de contacto',
                'field_type': 'mail',
                'required': True,
            },
        ],
    },
    {
        'form_name': 'Solicitud de información de intercambios académicos',
        'form_description': 'Solicitud de información sobre programas de intercambio académico',
        'form_information': (
            '¿Querés estar al tanto de las novedades de los intercambios para alumnos de FIUBA sin beca?'
            'Completá el siguiente formulario para que podamos mantenerte informado.'
        ),
        'form_procedure_value': 'Administrativo',
        'fields': [
            {
                'label': 'Correo',
                'field_type': 'mail',
                'required': True,
            },
            {
                'label': 'Nombre',
                'field_type': 'texto',
                'required': True,
            },
            {
                'label': 'Apellido',
                'field_type': 'texto',
                'required': True,
            },
            {
                'label': 'Padrón',
                'field_type': 'padron',
                'required': True,
            },
            {
                'label': 'Carrera',
                'field_type': 'catalog',
                'required': True,
                'catalog_key': 'carreras',
            },
            {
                'label': 'Promedio con CBC y aplazos',
                'field_type': 'numero',
                'required': True,
            },
            {
                'label': '¿Podrías realizar un intercambio sin la ayuda económica de una beca?',  
                'field_type': 'checkbox',
                'required': True,
            },
            {
                'label': '¿Cuántos créditos aprobados tenés?',
                'field_type': 'numero',
                'required': True,  
            },
            {
                'label': 'Correo electrónico FIUBA',
                'field_type': 'mail',
                'required': True,
            },
            {
                'label': '¿En qué cuatrimestre te gustaría irte de intercambio?',
                'field_type': 'texto',
                'required': True,
            },
            {
                'label': '¿Sabés a qué universidad te gustaría ir? En el instructivo que te pasé tenés el listado de universidades disponibles.',
                'field_type': 'texto',
                'required': True,
            },
            {
                'label': '¿A qué país te gustaría viajar?',
                'field_type': 'texto',
                'required': True,
            },
            {
                'label': '¿Tenes pensado postularte a alguna beca?',
                'field_type': 'checkbox',
                'required': False,
            },
            {
                'label': 'Tipo de beca',
                'field_type': 'catalog',
                'required': True,
                'catalog_key': 'tipo_de_beca',
            },
            {
                'label': 'Añadir programa de interés en caso de que no esté en las opciones anteriores',
                'field_type': 'texto',
                'required': False,
            },
            {
                'label': 'Subí tu analítico de materias aprobadas pedido en el Departamento de Alumnos (no obligatorio)',
                'field_type': 'adjunto',
                'required': False,
            }
        ],
    },
]


def seed_digital_email_form(apps, schema_editor):
    Form = apps.get_model('backend', 'Form')
    FormType = apps.get_model('backend', 'FormType')
    FormProcedureType = apps.get_model('backend', 'FormProcedureType')
    FormField = apps.get_model('backend', 'FormField')
    FormFieldType = apps.get_model('backend', 'FormFieldType')
    Catalog = apps.get_model('backend', 'Catalog')

    digital_type = FormType.objects.get(form_type_value='Digital')

    for digital_form in DIGITAL_FORMS:
        procedure = FormProcedureType.objects.get(
            form_procedure_value=digital_form['form_procedure_value']
        )

        form, created = Form.objects.get_or_create(
            form_name=digital_form['form_name'],
            defaults={
                'form_description': digital_form['form_description'],
                'form_information': digital_form['form_information'],
                'form_procedure': procedure,
                'form_type': digital_type,
            },
        )

        if not created:
            form.form_description = digital_form['form_description']
            form.form_information = digital_form['form_information']
            form.form_procedure = procedure
            form.form_type = digital_type
            form.save()

        FormField.objects.filter(form=form).delete()

        for order, field_data in enumerate(digital_form['fields'], start=1):
            field_type = FormFieldType.objects.get(
                form_field_type_value=field_data['field_type']
            )

            catalog = None
            if field_data.get('catalog_key'):
                catalog = Catalog.objects.get(catalog_key=field_data['catalog_key'])

            FormField.objects.create(
                form=form,
                form_field_label=field_data['label'],
                form_field_type=field_type,
                form_field_require=field_data['required'],
                form_field_order=order,
                catalog=catalog,
            )


def reverse_seed_digital_email_form(apps, schema_editor):
    Form = apps.get_model('backend', 'Form')
    Form.objects.filter(
        form_name__in=[digital_form['form_name'] for digital_form in DIGITAL_FORMS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0061_seed_document_forms'),
    ]

    operations = [
        migrations.RunPython(seed_digital_email_form, reverse_seed_digital_email_form),
    ]
