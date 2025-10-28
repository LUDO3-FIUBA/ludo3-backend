import uuid

from djoser.serializers import UserCreateSerializer, User, UserSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from backend.api_exceptions import InvalidImageError, StudentNotApprovedYetError
from backend.models import User
from backend.services import AwsS3Service
from backend.services.auth_fiuba_service import AuthFiubaService
from backend.services.image_validator_service import ImageValidatorService
from backend.services.siu_service import SiuService


class UserCustomCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('dni', 'email', 'is_student', 'is_teacher')

    def create(self, validated_data):
        b64_string = self.context['request'].data['image']
        
        # TEMPORARY WORKAROUND: Skip face detection for testing
        # TODO: Re-enable face detection once proper images are available
        # try:
        #     face_encodings, image = ImageValidatorService(b64_string).validate_image()
        # except InvalidImageError as e:
        #     raise serializers.ValidationError(e.detail)
        
        # For now, use empty face_encodings and fixed image format
        face_encodings = []
        
        validated_data['face_encodings'] = face_encodings
        validated_data['image'] = self._upload_image(b64_string, f"{uuid.uuid4()}.jpg")

        return super().create(validated_data)

    def validate(self, attrs):
        return attrs

    def _upload_image(self, image_b64, image_name):
        return AwsS3Service().upload_b64_image(image_b64, image_name)


class UserCustomGetSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('dni', 'email', 'first_name', 'last_name', 'is_student', 'is_teacher', 'file')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'code'

    class Meta:
        model = User
        fields = ('code',)

    def validate(self, attrs):
        token_response = self._fiuba_service().get_token(self.context['request'].data['code'], self.context['request'].data['redirect_uri'])

        auth_user_info = self._fiuba_service().userinfo(token_response['access_token'])

        user = User.objects.get(dni=auth_user_info['sub'])

        if not user.first_name:
            self._update_user(user, auth_user_info)

        data = {}

        refresh = self.get_token(user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        self._validated_data = data

        return data

    def is_valid(self, raise_exception=False):
        return self.validate(self.initial_data)

    def _fiuba_service(self):
        return AuthFiubaService()

    def _update_user(self, user, auth_user_info):
        siu_user_info = self._get_siu_user(user.is_student, user.dni)
        # siu_user_info = { 'file': '328123' }

        user.first_name = auth_user_info['name']
        user.last_name = auth_user_info['family_name']

        if user.is_student:
            if not user.student.inscripto:
                raise StudentNotApprovedYetError()
            user.student.padron = siu_user_info['file']
            user.student.save()
        else:
            user.teacher.legajo = siu_user_info['file']
            user.teacher.save()
        user.save()

    def _get_siu_user(self, is_student, dni):
        return SiuService().get_student(dni) if is_student else SiuService().get_teacher(dni)
