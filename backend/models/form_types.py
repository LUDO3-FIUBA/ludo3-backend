from django.db import models


class FormProcedureType(models.Model):
    form_procedure_value = models.CharField(max_length=100, verbose_name="Tipo de trámite")

    class Meta:
        verbose_name = "Tipo de trámite"
        verbose_name_plural = "Tipos de trámite"

    def __str__(self):
        return self.form_procedure_value


class FormType(models.Model):
    form_type_value = models.CharField(max_length=100, verbose_name="Tipo de formulario")

    class Meta:
        verbose_name = "Tipo de formulario"
        verbose_name_plural = "Tipos de formulario"

    def __str__(self):
        return self.form_type_value


class FormFieldType(models.Model):
    form_field_type_value = models.CharField(max_length=100, verbose_name="Tipo de campo")

    TEXTO = 'texto'
    NUMERO = 'numero'
    PADRON = 'padron'
    MAIL = 'mail'
    OPTIONS = 'options'
    CATALOG = 'catalog'
    CHECKBOX = 'checkbox'
    ADJUNTO = 'adjunto'

    class Meta:
        verbose_name = "Tipo de campo de formulario"
        verbose_name_plural = "Tipos de campo de formulario"

    def __str__(self):
        return self.form_field_type_value
