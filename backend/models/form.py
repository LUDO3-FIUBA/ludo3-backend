from django.db import models
from django.utils import timezone

from .catalog import Catalog
from .form_types import FormFieldType, FormProcedureType, FormType


class Form(models.Model):
    form_name = models.CharField(max_length=100, verbose_name="Nombre")
    form_description = models.CharField(max_length=300, verbose_name="Descripción")
    form_information = models.TextField(null=True, blank=True, verbose_name="Información adicional")
    form_procedure = models.ForeignKey(
        FormProcedureType, on_delete=models.CASCADE, related_name='forms', verbose_name="Tipo de trámite"
    )
    form_type = models.ForeignKey(
        FormType, on_delete=models.CASCADE, related_name='forms', verbose_name="Tipo de formulario"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Creado en")

    class Meta:
        verbose_name = "Formulario"
        verbose_name_plural = "Formularios"

    def __str__(self):
        return self.form_name


class FormDocumentSource(models.Model):
    form = models.OneToOneField(
        Form, on_delete=models.CASCADE, primary_key=True, related_name='document_source', verbose_name="Formulario"
    )
    form_document_source = models.URLField(verbose_name="URL del documento")

    class Meta:
        verbose_name = "Fuente de documento"
        verbose_name_plural = "Fuentes de documento"

    def __str__(self):
        return f"{self.form.form_name} — {self.form_document_source}"


class FormField(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='fields', verbose_name="Formulario")
    form_field_label = models.CharField(max_length=200, verbose_name="Etiqueta")
    form_field_type = models.ForeignKey(
        FormFieldType, on_delete=models.CASCADE, related_name='form_fields', verbose_name="Tipo de campo"
    )
    form_field_require = models.BooleanField(default=False, verbose_name="Obligatorio")
    form_field_order = models.IntegerField(verbose_name="Orden")
    catalog = models.ForeignKey(
        Catalog, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='form_fields', verbose_name="Catálogo"
    )

    class Meta:
        verbose_name = "Campo de formulario"
        verbose_name_plural = "Campos de formulario"
        ordering = ['form_field_order']

    def __str__(self):
        return f"{self.form.form_name} — {self.form_field_label}"


class FormFieldOption(models.Model):
    form_field = models.ForeignKey(
        FormField, on_delete=models.CASCADE, related_name='options', verbose_name="Campo"
    )
    form_option_value = models.CharField(max_length=100, verbose_name="Valor")
    form_option_label = models.CharField(max_length=200, verbose_name="Etiqueta")

    class Meta:
        verbose_name = "Opción de campo"
        verbose_name_plural = "Opciones de campo"

    def __str__(self):
        return f"{self.form_field.form_field_label} — {self.form_option_label}"
