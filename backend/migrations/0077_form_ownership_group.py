from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0076_secretary_and_staff_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormOwnershipGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Nombre')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Grupo de propiedad',
                'verbose_name_plural': 'Grupos de propiedad',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FormOwnershipMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_type', models.CharField(
                    choices=[('department', 'Departamento'), ('secretary', 'Secretaría')],
                    max_length=20,
                    verbose_name='Tipo de entidad',
                )),
                ('entity_id', models.IntegerField(verbose_name='ID de entidad')),
                ('is_editor', models.BooleanField(default=False, verbose_name='Es editor')),
                ('group', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='members',
                    to='backend.formownershipgroup',
                    verbose_name='Grupo',
                )),
            ],
            options={
                'verbose_name': 'Miembro del grupo',
                'verbose_name_plural': 'Miembros del grupo',
            },
        ),
        migrations.AddConstraint(
            model_name='formownershipmember',
            constraint=models.UniqueConstraint(
                fields=['group', 'entity_type', 'entity_id'],
                name='unique_group_entity',
            ),
        ),
        migrations.AddField(
            model_name='form',
            name='ownership_group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='forms',
                to='backend.formownershipgroup',
                verbose_name='Grupo de propiedad',
            ),
        ),
    ]
