import logging
import uuid

from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.serializers.user_serializer import (
    UserCustomCreateSerializer, UserCustomGetSerializer, SimpleLoginSerializer,
    UserGithubUrlSerializer)
from backend.services import AwsS3Service
from backend.services.image_validator_service import ImageValidatorService

from ..api_exceptions import InvalidFaceError, InvalidImageError
from ..models import User

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
            serializer = UserGithubUrlSerializer(request.user, data=request.data, partial=True)
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
                model.image = AwsS3Service().upload_b64_image(image, f"{uuid.uuid4()}.jpg")
            except Exception:
                logger.exception("S3 upload failed at register_face; face encodings saved without image URL.")

        model.save()
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

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
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


simple_login = SimpleLoginView.as_view()
