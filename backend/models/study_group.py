from django.db import models

from .student import Student


class StudyGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    creator = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Grupo de estudio"
        verbose_name_plural = "Grupos de estudio"

    def __str__(self):
        return f"{self.name} (creado por {self.creator})"


class GroupMembership(models.Model):
    class Status(models.TextChoices):
        PENDING = 'P', 'Pending'
        ACCEPTED = 'A', 'Accepted'

    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='memberships')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='group_memberships')
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PENDING)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Miembro de grupo"
        verbose_name_plural = "Miembros de grupo"
        constraints = [
            models.UniqueConstraint(fields=['group', 'student'], name='unique_group_member'),
        ]

    def __str__(self):
        return f"{self.student} → {self.group.name} ({self.status})"
