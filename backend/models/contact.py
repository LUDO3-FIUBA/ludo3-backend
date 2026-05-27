from django.db import models

from .student import Student


class Contact(models.Model):
    class Status(models.TextChoices):
        PENDING = 'P', 'Pending'
        ACCEPTED = 'A', 'Accepted'

    from_student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sent_contacts')
    to_student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='received_contacts')
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        constraints = [
            models.UniqueConstraint(fields=['from_student', 'to_student'], name='unique_contact_pair'),
        ]

    def __str__(self):
        return f"{self.from_student} → {self.to_student} ({self.status})"
