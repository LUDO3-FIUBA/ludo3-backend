import io

import qrcode
from django.conf import settings
from django.core import signing
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from backend.models import Student
from backend.permissions import IsStudent
from backend.serializers.student_identity_serializer import StudentIdentitySerializer
from backend.views.base_view import BaseViewSet

SIGNING_SALT = 'student-identity'
TOKEN_MAX_AGE = 86400  # 24 horas
TOKEN_MAX_AGE_HOURS = TOKEN_MAX_AGE // 3600


class StudentIdentityViewSet(BaseViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentIdentitySerializer

    def get_identity_link(self, student):
        token = signing.dumps({'padron': student.padron}, salt=SIGNING_SALT)
        return f"{settings.FRONTEND_BASE_URL}/credencial/{token}"

    def get_permissions(self):
        if self.action == 'identity':
            return [AllowAny()]
        return [IsAuthenticated(), IsStudent()]

    @action(detail=False, methods=['GET'], url_path='my_qr', url_name='my-qr')
    def my_qr(self, request):
        student = request.user.student
        identity_url = self.get_identity_link(student)
        qr = qrcode.make(identity_url)
        output = io.BytesIO()
        qr.save(output, format='PNG')
        return HttpResponse(output.getvalue(), content_type='image/png')

    @action(detail=False, methods=['GET'], url_path='my_identity_link', url_name='my-identity-link')
    def my_identity_link(self, request):
        student = request.user.student
        return Response({
            'url': self.get_identity_link(student),
            'expires_in_hours': TOKEN_MAX_AGE_HOURS,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'identity/(?P<token>[^/.]+)', url_name='identity')
    def identity(self, request, token=None):
        try:
            payload = signing.loads(token, salt=SIGNING_SALT, max_age=TOKEN_MAX_AGE)
        except (signing.SignatureExpired, signing.BadSignature):
            return Response({'detail': 'Token inválido o expirado.'}, status=status.HTTP_404_NOT_FOUND)
        student = get_object_or_404(Student, padron=payload['padron'])
        return Response(StudentIdentitySerializer(student).data, status=status.HTTP_200_OK)
