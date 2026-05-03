from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.permissions import permissions
from backend.serializers.teacher_serializer import TeacherSerializer
from backend.views.base_view import BaseViewSet

from ..models import Teacher


class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_teacher or request.user.is_staff


class TeacherViews(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    queryset = Teacher.objects.select_related('user').all()
    serializer_class = TeacherSerializer

    @swagger_auto_schema(
        tags=["Teachers"],
        operation_summary="Get a list of all teachers"
    )
    def list(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated],
            url_path='search')
    @swagger_auto_schema(
        tags=["Teachers"],
        operation_summary="Busca docentes por nombre o legajo (disponible para todos los usuarios autenticados)",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Texto a buscar en nombre, apellido o legajo")
        ],
    )
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        qs = Teacher.objects.select_related('user').all()
        if query:
            qs = qs.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(legajo__icontains=query)
            )
        return Response(TeacherSerializer(qs[:20], many=True).data)
