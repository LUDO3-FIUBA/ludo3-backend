from django.db import models


class Catalog(models.Model):
    catalog_key = models.CharField(max_length=100, unique=True, verbose_name="Clave")
    catalog_name = models.CharField(max_length=200, verbose_name="Nombre")
    catalog_description = models.TextField(null=True, blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Catálogo"
        verbose_name_plural = "Catálogos"

    def __str__(self):
        return self.catalog_name


class CatalogItem(models.Model):
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name='items', verbose_name="Catálogo")
    catalog_item_value = models.CharField(max_length=100, verbose_name="Valor")
    catalog_item_label = models.CharField(max_length=200, verbose_name="Etiqueta")
    catalog_item_order = models.IntegerField(null=True, blank=True, verbose_name="Orden")
    catalog_item_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Item de catálogo"
        verbose_name_plural = "Items de catálogo"
        ordering = ['catalog_item_order', 'id']

    def __str__(self):
        return f"{self.catalog.catalog_name} — {self.catalog_item_label}"
