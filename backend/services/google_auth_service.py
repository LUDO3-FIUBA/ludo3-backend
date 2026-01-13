import logging
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from backend.client.google_auth_client import GoogleAuthClient
from backend.models.auth_identity import AuthIdentity
from backend.models.student import Student
from backend.models.teacher import Teacher

logger = logging.getLogger(__name__)
User = get_user_model()


class GoogleAuthService:
    def __init__(self):
        self.client = GoogleAuthClient()

    def authenticate(self, id_token):
        claims = self.client.verify_token(id_token)
        
        sub = claims.get("sub")
        email = claims.get("email")
        
        if not sub or not email:
            raise ValidationError("Invalid Google ID token: missing sub or email")
        
        identity = AuthIdentity.objects.select_related("user").filter(
            provider=AuthIdentity.Provider.GOOGLE,
            provider_user_id=sub,
        ).first()

        if identity:
            return {
                'status': 'existing_user',
                'user': identity.user,
            }
        
        if AuthIdentity.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email is already registered.")
                
        return {
            'status': 'needs_registration',
            'google_data': {
                'sub': sub,
                'email': email,
                'first_name': claims.get("given_name", ""),
                'last_name': claims.get("family_name", ""),
            }
        }

    def complete_registration(self, sub, email, dni, padron=None, first_name='', last_name='', 
                             is_student=True, is_teacher=False):

        if AuthIdentity.objects.filter(provider=AuthIdentity.Provider.GOOGLE, provider_user_id=sub).exists():
            raise ValidationError("This Google account is already registered")
        
        if AuthIdentity.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered")
        
        if User.objects.filter(dni=dni).exists():
            raise ValidationError("This DNI is already registered")
        
        user = User(
            email=email,
            dni=dni,
            first_name=first_name,
            last_name=last_name,
            is_student=is_student,
            is_teacher=is_teacher,
            username=email,
        )
        user.set_unusable_password()
        user.save()
        
        if is_student:
            Student.objects.create(user=user, padron=padron, face_encodings=[])
        elif is_teacher:
            Teacher.objects.create(user=user, face_encodings=[])
        
        AuthIdentity.objects.create(
            user=user,
            provider=AuthIdentity.Provider.GOOGLE,
            provider_user_id=sub,
            email=email,
        )
        
        return user