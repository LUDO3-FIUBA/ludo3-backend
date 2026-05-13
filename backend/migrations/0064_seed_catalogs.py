from django.db import migrations


CATALOGS = [
    {
        'catalog_key': 'rol_en_comunidad',
        'catalog_name': 'Rol en la comunidad',
        'items': [
            'Alumno de Grado',
            'Alumno de Posgrado',
            'Alumno de Intercambio',
            'Graduado',
            'Docente',
            'Docente de Posgrado',
            'Investigador',
            'No Docente',
            'Contrato de Servicios',
            'Autoridad',
            'CBC',
            'Alumno no regular/ ex alumno',
        ],
    },
    {
        'catalog_key': 'carreras',
        'catalog_name': 'Carreras',
        'items': [
            'Ing. Civil',
            'Ing. de Alimentos',
            'Ing. en Energía Eléctrica',
            'Ing. Electrónica',
            'Ing. en Agrimensura',
            'Ing. en Informática',
            'Ing. en Petróleo',
            'Ing. Industrial',
            'Ing. Mecánica',
            'Ing. Naval y Mecánica',
            'Ing. Química',
            'Lic. en Análisis de Sistemas',
            'Bioingeniería',
        ],
    },
    {
        'catalog_key': 'tipo_de_beca',
        'catalog_name': 'Tipo de beca',
        'items': [
            'Doble Diploma',
            'Programa UBAInt',
            'Programa AUGM',
            'Programa "convocatoria unificada"',
            'Beca Aelarg',
            'Programa sin beca',
        ],
    }
]


def seed_catalogs(apps, schema_editor):
    Catalog = apps.get_model('backend', 'Catalog')
    CatalogItem = apps.get_model('backend', 'CatalogItem')

    for catalog_data in CATALOGS:
        catalog, _ = Catalog.objects.get_or_create(
            catalog_key=catalog_data['catalog_key'],
            defaults={'catalog_name': catalog_data['catalog_name']},
        )
        for order, label in enumerate(catalog_data['items'], start=1):
            CatalogItem.objects.get_or_create(
                catalog=catalog,
                catalog_item_label=label,
                defaults={
                    'catalog_item_value': label,
                    'catalog_item_order': order,
                },
            )


def reverse_seed_catalogs(apps, schema_editor):
    Catalog = apps.get_model('backend', 'Catalog')
    Catalog.objects.filter(
        catalog_key__in=[c['catalog_key'] for c in CATALOGS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0063_form_teacher_validation'),
    ]

    operations = [
        migrations.RunPython(seed_catalogs, reverse_seed_catalogs),
    ]
