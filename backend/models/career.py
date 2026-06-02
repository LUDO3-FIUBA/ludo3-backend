from django.db import models


class Career(models.Model):
    siu_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'
