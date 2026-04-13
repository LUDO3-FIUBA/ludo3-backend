import logging

import requests
from django.conf import settings

from backend.api_exceptions import ValidationError

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_password_reset_code(email, code):
        if not settings.RESEND_API_KEY:
            logger.warning('RESEND_API_KEY not configured. Skipping email send.')
            return False

        payload = {
            'from': settings.RESEND_FROM_EMAIL,
            'to': [email],
            'subject': 'Recuperación de contraseña - LUDO',
            'html': (
                '<p>Recibimos una solicitud para recuperar tu contraseña.</p>'
                f'<p>Tu código es: <strong>{code}</strong></p>'
                f'<p>Este código vence en {settings.PASSWORD_RESET_CODE_TTL_MINUTES} minutos.</p>'
                '<p>Si no fuiste vos, ignorá este mensaje.</p>'
            ),
        }

        response = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {settings.RESEND_API_KEY}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=10,
        )

        if response.status_code >= 400:
            logger.error('Resend error sending email: %s - %s', response.status_code, response.text)
            raise ValidationError('No se pudo enviar el correo de recuperación')

        return True
