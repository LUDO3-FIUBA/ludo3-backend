import hashlib
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from backend.models import PasswordResetOTP
from backend.serializers.password_serializer import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordConfirmSerializer,
)
from backend.services.email_service import EmailService


def _generate_code():
    return str(random.randint(100000, 999999))


def _otp_expiration():
    return timezone.now() + timedelta(minutes=settings.PASSWORD_RESET_CODE_TTL_MINUTES)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    request.user.set_password(serializer.validated_data['new_password'])
    request.user.save(update_fields=['password'])

    return Response({'message': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']
    response_body = {
        'message': 'Si el usuario existe, se envió un código de recuperación',
    }

    if not user:
        return Response(response_body, status=status.HTTP_200_OK)

    PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True, updated_at=timezone.now())

    code = _generate_code()
    otp = PasswordResetOTP.objects.create(
        user=user,
        code_hash=hashlib.sha256(code.encode('utf-8')).hexdigest(),
        expires_at=_otp_expiration(),
        max_attempts=settings.PASSWORD_RESET_MAX_ATTEMPTS,
    )

    EmailService.send_password_reset_code(user.email, code)

    if settings.DEBUG:
        response_body['debug_code'] = code
        response_body['otp_id'] = otp.id

    return Response(response_body, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    serializer = ResetPasswordConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']
    code = serializer.validated_data['code']
    new_password = serializer.validated_data['new_password']

    otp = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()

    if not otp or not otp.can_attempt():
        return Response({'code': ['Código inválido o vencido']}, status=status.HTTP_400_BAD_REQUEST)

    if not otp.check_code(code):
        otp.register_failed_attempt()
        return Response({'code': ['Código inválido o vencido']}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save(update_fields=['password'])
    otp.mark_used()

    return Response({'message': 'Contraseña restablecida correctamente'}, status=status.HTTP_200_OK)
