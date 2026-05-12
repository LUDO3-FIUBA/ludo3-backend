from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import User
from backend.models.student import Student
from backend.models.teacher import Teacher
from backend.permissions import IsSuperAdmin
from backend.serializers.user_admin_serializer import (
    UserAdminReadSerializer,
    UserAdminWriteSerializer,
)
from backend.views.base_view import BaseViewSet


class UserAdminViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminReadSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Users Admin"],
        operation_summary="Search users by DNI",
        manual_parameters=[
            openapi.Parameter(
                'dni', openapi.IN_QUERY,
                description="DNI (exact or partial match)",
                type=openapi.TYPE_STRING, required=True,
            )
        ],
    )
    def search(self, request):
        dni = request.query_params.get('dni', '').strip()
        if not dni:
            return Response(
                {"detail": "El parámetro 'dni' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        users = self.get_queryset().filter(dni__icontains=dni)[:20]
        return Response(UserAdminReadSerializer(users, many=True).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["Users Admin"], operation_summary="Get user detail")
    def retrieve(self, request, pk=None, *args, **kwargs):
        user = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(UserAdminReadSerializer(user).data, status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Users Admin"],
        operation_summary="Update a user (admins cannot be modified)",
        request_body=UserAdminWriteSerializer,
    )
    def partial_update(self, request, pk=None, *args, **kwargs):
        user = get_object_or_404(self.get_queryset(), pk=pk)

        if user.is_staff:
            return Response(
                {"detail": "No se puede modificar un usuario administrador."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserAdminWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Update basic user fields
        for field in ('first_name', 'last_name', 'email', 'dni'):
            if field in data and data[field]:
                setattr(user, field, data[field])

        # Update student-specific fields
        if user.is_student and 'padron' in data and data['padron']:
            user.student.padron = data['padron']
            user.student.save()

        # Update teacher-specific fields
        if user.is_teacher and 'legajo' in data and data['legajo']:
            user.teacher.legajo = data['legajo']
            user.teacher.save()

        # Promote student → also teacher
        if data.get('promote_to_teacher') and not user.is_teacher:
            new_legajo = data.get('new_legajo', '')
            if not new_legajo:
                return Response(
                    {"detail": "Se requiere 'new_legajo' para promover a docente."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_teacher = True
            Teacher(user=user, legajo=new_legajo, face_encodings=[]).save()

        # Promote teacher → also student
        if data.get('promote_to_student') and not user.is_student:
            new_padron = data.get('new_padron', '')
            if not new_padron:
                return Response(
                    {"detail": "Se requiere 'new_padron' para promover a estudiante."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_student = True
            Student(user=user, padron=new_padron, face_encodings=[], image=None).save()

        user.save()
        return Response(UserAdminReadSerializer(user).data, status.HTTP_200_OK)
