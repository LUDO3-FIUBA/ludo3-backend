from django.db import migrations


DOCUMENT_FORMS = [
    {
        'form_name': 'Nota al decano',
        'form_description': 'Carta particular para un pedido al decano de la facultad',
        'form_procedure_value': 'Administrativo',
        'url': 'https://cms.fi.uba.ar/uploads/Nota_al_Decano_6b8cf05977_2e9fd6c866.pdf',
    },
    {
        'form_name': 'Certificado de alumno regular',
        'form_description': 'Pedido de certificado de regularidad',
        'form_procedure_value': 'Administrativo',
        'url': 'https://cms.fi.uba.ar/uploads/Certificado_de_Alumno_Regular_e33f4be349_77f1380569.pdf',
    },
    {
        'form_name': 'Certificado de trámite en curso',
        'form_description': 'Certificado para dar validez a un trámite en curso para presentar ante otras autoridades',
        'form_procedure_value': 'Administrativo',
        'url': 'https://cms.fi.uba.ar/uploads/Solicitud_de_Tramite_en_Curso_b3061e3932_c65a7c15c9.pdf',
    },
    {
        'form_name': 'Constancia de examen',
        'form_description': 'Constancia de haber rendido un exámen para presentar ante otras autoridades',
        'form_procedure_value': 'Exámenes',
        'url': 'https://cms.fi.uba.ar/uploads/CONSTANCIA_POR_RENDIR_EXAMEN_2022_830adf5424.pdf',
    },
    {
        'form_name': 'Mesa Especial',
        'form_description': 'Solicitud para rendir examen en mesa especial',
        'form_procedure_value': 'Exámenes',
        'url': 'https://cms.fi.uba.ar/uploads/Solicitud_de_Mesa_Especial_2d3fcf2db9_19bed8a95e.pdf',
    },
    {
        'form_name': 'Pedido de Prórroga de asignatura vencida',
        'form_description': 'Solucitud para extender el vencimiento de una asignatura aprobada',
        'form_procedure_value': 'Exámenes',
        'url': 'https://cms.fi.uba.ar/uploads/Pedido_de_prorroga_2016_6d3c73103b_a7b853a6bd.pdf',
    },
    {
        'form_name': 'Pase de carrera en FIUBA',
        'form_description': 'Cambiar de carrera dentro de FIUBA',
        'form_procedure_value': 'Carrera',
        'url': 'https://cms.fi.uba.ar/uploads/Solicitud_de_Pase_de_Carrera_dentro_de_la_Fiuba_aff49f97e4_62f69042b7.pdf',
    },
    {
        'form_name': 'Simultaneidad en FIUBA',
        'form_description': 'Cursar otra carrera en simultáneo en FIUBA',
        'form_procedure_value': 'Carrera',
        'url': 'https://cms.fi.uba.ar/uploads/Solicitud_de_Simultaneidad_de_Carrera_dentro_de_la_Fiuba_2b597195d5_08d2551b2e.pdf',
    },
    {
        'form_name': 'Pase/Simultaneidad en UBA',
        'form_description': 'Pase o simultaneidad a otra carrera de la UBA',
        'form_procedure_value': 'Carrera',
        'url': 'https://cms.fi.uba.ar/uploads/PASE_SIMULTANEIDAD_UBA_2020_9a5555a468_daf7433680.pdf',
    },
    {
        'form_name': 'Excepción de correlatividad',
        'form_description': 'Pedido de excepción de correlatividad',
        'form_procedure_value': 'Cursada',
        'url': 'https://cms.fi.uba.ar/uploads/Pedido_de_excepcion_2016_f77cee96e0_b6a398efe5.pdf',
    },
    {
        'form_name': 'Reconocimiento de créditos',
        'form_description': 'Reconocimiento de créditos por actividad académica',
        'form_procedure_value': 'Cursada',
        'url': 'https://cms.fi.uba.ar/uploads/Solicitud_de_Reconocimiento_de_Creditos_760738bc28_698d0ec3c7.pdf',
    },
    {
        'form_name': 'Readmisión como alumno regular',
        'form_description': 'Recuperar carácter de alumno regular',
        'form_procedure_value': 'Cursada',
        'url': 'https://cms.fi.uba.ar/uploads/Readmision_como_Alumno_Regular_2020_6ace3ffae2_6fd804deac.pdf',
    },
    {
        'form_name': 'Resolución 168',
        'form_description': 'Régimen especial Resolución 168/58',
        'form_procedure_value': 'Cursada',
        'url': 'https://cms.fi.uba.ar/uploads/Formulario_para_cursar_por_RES_168_2020_795aabfb00_236ff3effe.pdf',
    },
]


def seed_document_forms(apps, schema_editor):
    Form = apps.get_model('backend', 'Form')
    FormType = apps.get_model('backend', 'FormType')
    FormProcedureType = apps.get_model('backend', 'FormProcedureType')
    FormDocumentSource = apps.get_model('backend', 'FormDocumentSource')
    FormField = apps.get_model('backend', 'FormField')
    FormFieldType = apps.get_model('backend', 'FormFieldType')

    documento_type = FormType.objects.get(form_type_value='Documento')
    adjunto_type = FormFieldType.objects.filter(form_field_type_value='adjunto').first()

    for data in DOCUMENT_FORMS:
        procedure = FormProcedureType.objects.get(form_procedure_value=data['form_procedure_value'])
        form = Form.objects.create(
            form_name=data['form_name'],
            form_description=data['form_description'],
            form_procedure=procedure,
            form_type=documento_type,
        )
        FormDocumentSource.objects.create(form=form, form_document_source=data['url'])
        FormField.objects.create(
            form=form,
            form_field_label='Adjunto',
            form_field_type=adjunto_type,
            form_field_require=True,
            form_field_order=1,
        )


def reverse_seed_document_forms(apps, schema_editor):
    Form = apps.get_model('backend', 'Form')
    Form.objects.filter(form_name__in=[d['form_name'] for d in DOCUMENT_FORMS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0059_seed_catalogs'),
    ]

    operations = [
        migrations.RunPython(seed_document_forms, reverse_seed_document_forms),
    ]
