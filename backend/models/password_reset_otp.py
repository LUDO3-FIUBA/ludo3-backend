import hashlib
import secrets

from django.db import models
from django.utils import timezone

from .user import User


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        User,
        related_name='password_reset_otps',
        on_delete=models.CASCADE,
    )
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Código recuperación de contraseña'
        verbose_name_plural = 'Códigos recuperación de contraseña'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['expires_at']),
        ]

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=['is_used', 'updated_at'])

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def can_attempt(self):
        return (not self.is_used) and (not self.is_expired()) and self.attempts < self.max_attempts

    def register_failed_attempt(self):
        self.attempts += 1
        self.save(update_fields=['attempts', 'updated_at'])

    def check_code(self, plain_code):
        provided_hash = hashlib.sha256(plain_code.encode('utf-8')).hexdigest()
        return secrets.compare_digest(self.code_hash, provided_hash)
