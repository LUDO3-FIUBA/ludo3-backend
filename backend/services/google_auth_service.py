import logging
import os
from django.contrib.auth import get_user_model
import time
from backend.api_exceptions import ValidationError

from backend.client.google_auth_client import GoogleAuthClient
from backend.client.guarani_client import GuaraniClient
from backend.models.auth_identity import AuthIdentity
from backend.models.student import Student
from backend.models.teacher import Teacher

logger = logging.getLogger(__name__)
User = get_user_model()

GUARANI_DNI_TIPO_DOCUMENTO = 0


class GoogleAuthService:
    ALLOWED_DOMAINS = {'fi.uba.ar'}
    ALLOWED_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}

    def __init__(self):
        self.client = GoogleAuthClient()

    def authenticate(self, id_token):
        claims = self.client.verify_token(id_token)
        sub, email = self._validate_google_claims(claims)

        identity = AuthIdentity.objects.select_related("user").filter(
            provider=AuthIdentity.Provider.GOOGLE,
            provider_user_id=sub,
        ).first()

        if identity:
            return {
                'status': 'existing_user',
                'user': identity.user,
            }

        self._validate_new_identity_constraints(sub=sub, email=email)
                
        return {
            'status': 'needs_registration',
            'google_data': {
                'sub': sub,
                'email': email,
                'first_name': claims.get("given_name", ""),
                'last_name': claims.get("family_name", ""),
            }
        }

    def complete_registration(self, sub, email, dni, password, padron=None, first_name='', last_name='',
                             is_student=True, is_teacher=False):
        self._validate_new_identity_constraints(sub=sub, email=email, dni=dni)

        if is_student:
            self._verify_dni_email_with_guarani(dni=dni, google_email=email)

        user = User(
            email=email,
            dni=dni,
            first_name=first_name,
            last_name=last_name,
            is_student=is_student,
            is_teacher=is_teacher,
            username=email,
        )
        if not password:
            raise ValidationError("Password is required")
        user.set_password(password)
        user.save()
        
        if is_student:
            Student.objects.create(user=user, padron=padron, face_encodings=[])
        if is_teacher:
            Teacher.objects.create(user=user, face_encodings=[])
        
        AuthIdentity.objects.create(
            user=user,
            provider=AuthIdentity.Provider.GOOGLE,
            provider_user_id=sub,
            email=email,
        )
        
        return user

    def _validate_google_claims(self, claims):
        if not claims.get("email_verified"):
            raise ValidationError("Email not verified by Google")

        iss = claims.get("iss")
        if iss not in self.ALLOWED_ISSUERS:
            raise ValidationError("Invalid issuer")

        expected_audience = self.client.GOOGLE_CLIENT_ID
        if claims.get("aud") != expected_audience:
            raise ValidationError("Invalid audience")

        sub = claims.get("sub")
        email = claims.get("email")
        if not sub or not email:
            raise ValidationError("Invalid Google ID token: missing sub or email")

        hd = claims.get("hd")
        if hd and hd not in self.ALLOWED_DOMAINS:
            raise ValidationError("Hosted domain not allowed")

        exp = claims.get("exp")
        if not exp or exp < time.time():
            raise ValidationError("Token expired")

        return sub, email

    def _validate_new_identity_constraints(self, sub, email, dni=None):
        if AuthIdentity.objects.filter(provider=AuthIdentity.Provider.GOOGLE, provider_user_id=sub).exists():
            raise ValidationError("This Google account is already registered")

        if AuthIdentity.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered")

        if dni and User.objects.filter(dni=dni).exists():
            raise ValidationError("This DNI is already registered")

    def _verify_dni_email_with_guarani(self, dni, google_email):
        try:
            alumno = GuaraniClient().get_alumno(GUARANI_DNI_TIPO_DOCUMENTO, dni)
        except Exception:
            logger.exception("Guaraní lookup failed for DNI %s", dni)
            raise ValidationError("No se pudo verificar el DNI con SIU Guaraní. Intentá de nuevo.")

        if not alumno:
            raise ValidationError("No se encontró un alumno con ese DNI en SIU Guaraní.")

        guarani_email = (alumno.get('email') or '').strip() if isinstance(alumno, dict) else ''
        if not guarani_email:
            raise ValidationError("El alumno no tiene un email registrado en SIU Guaraní.")

        if guarani_email.lower() != (google_email or '').strip().lower():
            raise ValidationError("El email de Google no coincide con el registrado en SIU Guaraní.")