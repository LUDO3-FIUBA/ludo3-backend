from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from backend.models import User


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    dni = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        dni = attrs.get('dni')
        if not email and not dni:
            raise serializers.ValidationError('Debe enviar email o dni')

        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
        elif dni:
            user = User.objects.filter(dni=dni).first()

        attrs['user'] = user
        return attrs


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    dni = serializers.CharField(required=False)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        dni = attrs.get('dni')
        if not email and not dni:
            raise serializers.ValidationError('Debe enviar email o dni')

        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
        elif dni:
            user = User.objects.filter(dni=dni).first()

        if user is None:
            raise serializers.ValidationError({'code': 'Código inválido'})

        try:
            validate_password(attrs['new_password'], user=user)
        except DjangoValidationError as exception:
            raise serializers.ValidationError({'new_password': exception.messages})

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Contraseña actual incorrecta'})

        try:
            validate_password(attrs['new_password'], user=user)
        except DjangoValidationError as exception:
            raise serializers.ValidationError({'new_password': exception.messages})

        return attrs
