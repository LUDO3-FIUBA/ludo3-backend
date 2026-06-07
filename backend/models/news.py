from django.db import models
from django.utils import timezone

from backend.news_tags import NEWS_TAG_CHOICES

from .department import Department
from .user import User


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, default='', verbose_name="Descripción")
    image = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name="Imagen")
    tag = models.CharField(max_length=50, choices=NEWS_TAG_CHOICES, verbose_name="Categoría")
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posted_news',
        verbose_name="Autor",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news',
        verbose_name="Departamento",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Novedad"
        verbose_name_plural = "Novedades"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
