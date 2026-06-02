import logging
import uuid

from djoser.serializers import UserCreateSerializer, User, UserSerializer
from rest_framework import serializers

from backend.api_exceptions import InvalidImageError
from backend.client.guarani_client import GuaraniClient
from backend.models import User
from backend.services import storage_service
from backend.services.image_validator_service import ImageValidatorService

logger = logging.getLogger(__name__)

GUARANI_DNI_TIPO_DOCUMENTO = 0


def fetch_alumno_email_from_guarani(dni):
    """Look up an alumno by DNI in SIU Guaraní and return their email.

    Raises ValidationError if the alumno is not found, the API call fails,
    or the alumno has no email registered.
    """
    try:
        alumno = GuaraniClient().get_alumno(GUARANI_DNI_TIPO_DOCUMENTO, dni)
    except Exception:
        logger.exception("Guaraní lookup failed for DNI %s", dni)
        raise serializers.ValidationError({
            'dni': 'No se pudo verificar el DNI con SIU Guaraní. Intentá de nuevo.'
        })

    if not alumno:
        raise serializers.ValidationError({
            'dni': 'No se encontró un alumno con ese DNI en SIU Guaraní.'
        })

    email = (alumno.get('email') or '').strip() if isinstance(alumno, dict) else ''
    if not email:
        raise serializers.ValidationError({
            'dni': 'El alumno no tiene un email registrado en SIU Guaraní.'
        })

    return email


class UserCustomCreateSerializer(UserCreateSerializer):
    # Campo padron no está en User, lo definimos explícitamente
    padron = serializers.CharField(
        required=False,
        min_length=5,
        max_length=7,
        help_text="Padrón del estudiante (5 a 7 dígitos)"
    )
    # Email is not required from the client — it's fetched from SIU Guaraní by DNI for students.
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('dni', 'email', 'is_student', 'is_teacher', 'padron', 'password')

    def validate(self, attrs):
        is_student = attrs.get('is_student', False)
        padron = attrs.get('padron')
        password = attrs.get('password')
        dni = attrs.get('dni')

        if is_student:
            if not padron:
                raise serializers.ValidationError({'padron': 'El padrón es obligatorio para estudiantes'})
            if not padron.isdigit():
                raise serializers.ValidationError({'padron': 'El padrón debe contener solo números'})
            if not password:
                raise serializers.ValidationError({'password': 'La contraseña es obligatoria para estudiantes'})

            # Fetch email from SIU Guaraní; ignore any email the client sent.
            attrs['email'] = fetch_alumno_email_from_guarani(dni)
        else:
            if not attrs.get('email'):
                raise serializers.ValidationError({'email': 'El email es obligatorio.'})

        return attrs

    def create(self, validated_data):
        b64_string = self.context['request'].data.get('image') if 'request' in self.context else None

        face_encodings = []
        image_url = None

        if b64_string:
            try:
                face_encodings, _ = ImageValidatorService(b64_string).validate_image()
            except InvalidImageError:
                # Registro facial fallido: dejamos al usuario registrarse y completar la foto después.
                logger.warning("Face detection failed at registration; user will need to complete face registration later.")
                face_encodings = []

            try:
                image_url = self._upload_image(b64_string, f"{uuid.uuid4()}.jpg")
            except Exception:
                logger.exception("S3 upload failed at registration; continuing without image URL.")
                image_url = None

        validated_data['face_encodings'] = face_encodings
        if image_url is not None:
            validated_data['image'] = image_url

        return super().create(validated_data)

    def _upload_image(self, image_b64, image_name):
        return storage_service.upload_b64_image(image_b64, image_name)


class UserCustomGetSerializer(UserSerializer):
    legajo = serializers.SerializerMethodField()
    face_registered = serializers.SerializerMethodField()
    department_id = serializers.SerializerMethodField()
    secretary_id = serializers.SerializerMethodField()
    is_bedelia = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('dni', 'email', 'first_name', 'last_name', 'is_student', 'is_teacher', 'is_staff', 'is_superuser', 'is_bedelia', 'department_id', 'secretary_id', 'file', 'legajo', 'github_url', 'linkedin_url', 'face_registered')

    def get_legajo(self, obj):
        if obj.is_teacher:
            return obj.teacher.legajo
        return None

    def get_face_registered(self, obj):
        if obj.is_student:
            return bool(getattr(obj, 'student', None) and obj.student.face_encodings)
        if obj.is_teacher:
            return bool(getattr(obj, 'teacher', None) and obj.teacher.face_encodings)
        return False

    def get_department_id(self, obj):
        if not obj.is_staff or obj.is_superuser:
            return None
        staff = getattr(obj, 'staff', None)
        return staff.department_id if staff else None

    def get_secretary_id(self, obj):
        if not obj.is_staff or obj.is_superuser:
            return None
        staff = getattr(obj, 'staff', None)
        return staff.secretary_id if staff else None

    def get_is_bedelia(self, obj):
        if not obj.is_staff or obj.is_superuser:
            return False
        staff = getattr(obj, 'staff', None)
        return bool(staff and staff.is_bedelia)


class UserMeUpdateSerializer(serializers.ModelSerializer):
    """Editable profile fields on the /me PATCH endpoint."""
    class Meta:
        model = User
        fields = ('github_url', 'linkedin_url')


class SimpleLoginSerializer(serializers.Serializer):
    dni = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        dni = attrs.get('dni')
        password = attrs.get('password')

        try:
            user = User.objects.get(dni=dni)
        except User.DoesNotExist:
            raise serializers.ValidationError({'dni': 'Usuario no encontrado'})

        # Validar contraseña
        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Contraseña incorrecta'})

        # Generar tokens JWT
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return data
