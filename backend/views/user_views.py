from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES

from backend.serializers.user_serializer import (
    CustomTokenObtainPairSerializer, UserCustomCreateSerializer,
    UserCustomGetSerializer, SimpleLoginSerializer)
from backend.services.image_validator_service import ImageValidatorService

from ..api_exceptions import InvalidFaceError, InvalidToken
from ..models import User


class UserCustomViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserCustomCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return UserCustomCreateSerializer

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def is_me(self, request):
        if not request.data.get('image'):
            raise InvalidFaceError()

        result = ImageValidatorService(request.data['image']).validate_identity(request.user.student)
        return Response({"match": result}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserCustomGetSerializer(instance)
        return Response(serializer.data)


class CustomTokenObtainPairView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = CustomTokenObtainPairSerializer

    www_authenticate_realm = 'api'

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class TokenError(Exception):
    pass


token_obtain_pair = CustomTokenObtainPairView.as_view()


class SimpleLoginView(GenericAPIView):
    """
    Vista de login simple sin OAuth de FIUBA.
    Permite autenticarse con DNI (y opcionalmente contraseña).
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = SimpleLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


simple_login = SimpleLoginView.as_view()
