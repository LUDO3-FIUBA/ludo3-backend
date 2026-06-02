import logging
import os
import uuid

from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.serializers.user_serializer import (
    UserCustomCreateSerializer, UserCustomGetSerializer, SimpleLoginSerializer,
    UserMeUpdateSerializer)
from backend.services import storage_service
from backend.services.image_validator_service import ImageValidatorService

from ..api_exceptions import InvalidFaceError, InvalidImageError
from ..models import User
from .cookie_auth_views import is_web_client, set_refresh_cookie


def _ext(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext if ext else '.jpg'

logger = logging.getLogger(__name__)


class UserCustomViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserCustomCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return UserCustomCreateSerializer

    @action(["get", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == "PATCH":
            serializer = UserMeUpdateSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserCustomGetSerializer(request.user).data, status=status.HTTP_200_OK)

        return Response(UserCustomGetSerializer(request.user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def is_me(self, request):
        if not request.data.get('image'):
            raise InvalidFaceError()

        result = ImageValidatorService(request.data['image']).validate_identity(request.user.student)
        return Response({"match": result}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def register_face(self, request):
        image = request.data.get('image')
        if not image:
            raise InvalidImageError(detail="Falta la imagen.")

        user = request.user
        if user.is_student:
            model = user.student
        elif user.is_teacher:
            model = user.teacher
        else:
            return Response(
                {"detail": "Solo estudiantes o docentes pueden registrar una foto."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        face_encodings, _ = ImageValidatorService(image).validate_image()
        model.face_encodings = face_encodings

        if user.is_student:
            try:
                model.image = storage_service.upload_b64_image(image, f"{uuid.uuid4()}.jpg")
            except Exception:
                logger.exception("S3 upload failed at register_face; face encodings saved without image URL.")

        model.save()
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def upload_profile_photo(self, request):
        from django.conf import settings as django_settings
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"detail": "Falta la imagen."}, status=status.HTTP_400_BAD_REQUEST)

        file_name = f"profile_photos/{uuid.uuid4()}{_ext(image_file.name)}"
        try:
            if getattr(django_settings, 'STORAGE_PROVIDER', 'local') == 'local':
                storage_service.upload_object(image_file, file_name)
                # Use request.build_absolute_uri so the URL reflects the actual host/port,
                # independent of the BASE_URL env var.
                url = request.build_absolute_uri(f"{django_settings.MEDIA_URL}{file_name}")
            else:
                url = storage_service.upload_object(image_file, file_name)
        except Exception:
            logger.exception("Upload failed for profile photo.")
            return Response({"detail": "No se pudo subir la imagen."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        request.user.profile_photo = url
        request.user.save(update_fields=['profile_photo'])
        return Response(UserCustomGetSerializer(request.user).data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserCustomGetSerializer(instance)
        return Response(serializer.data)


class SimpleLoginView(GenericAPIView):
    """
    Vista de login simple.
    Permite autenticarse con DNI y contraseña.
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = SimpleLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if is_web_client(request):
            response = Response({'access': data['access']}, status=status.HTTP_200_OK)
            set_refresh_cookie(response, data['refresh'])
        else:
            response = Response(data, status=status.HTTP_200_OK)

        return response


simple_login = SimpleLoginView.as_view()
