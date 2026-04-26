from django.db import models
from django.utils import timezone

from .user import User

class AuthIdentity(models.Model):
    class Provider(models.TextChoices):
        LOCAL = "local", "Local"
        GOOGLE = "google", "Google"

    user = models.OneToOneField(User, related_name="auth_identity", on_delete=models.CASCADE)
    provider = models.CharField(max_length=32, choices=Provider.choices)
    provider_user_id = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    added_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["provider", "provider_user_id"], name="unique_identity_per_provider"),
        ]

    def __str__(self):
        return f"{self.provider}:{self.provider_user_id} → {self.user_id}"