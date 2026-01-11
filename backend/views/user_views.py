from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.serializers.user_serializer import (
    UserCustomCreateSerializer, UserCustomGetSerializer, SimpleLoginSerializer)
from backend.services.image_validator_service import ImageValidatorService

from ..api_exceptions import InvalidFaceError
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
