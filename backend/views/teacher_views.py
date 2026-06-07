from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.permissions import IsTeacherOrAdmin
from backend.serializers.teacher_serializer import (TeacherProfileSerializer,
                                                    TeacherSerializer)
from backend.views.base_view import BaseViewSet
from backend.views.utils import get_current_semester, get_current_year

from ..models import Commission, CommissionInscription, Teacher


class TeacherViews(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    queryset = Teacher.objects.select_related('user').all()
    serializer_class = TeacherSerializer

    @swagger_auto_schema(
        tags=["Teachers"],
        operation_summary="Listar todos los docentes"
    )
    def list(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Teachers"],
        operation_summary="Busca docentes por nombre o legajo (disponible para todos los usuarios autenticados)",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Texto a buscar en nombre, apellido o legajo")
        ],
    )
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated],
            url_path='search')
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

    @swagger_auto_schema(
        tags=["Teachers"],
        operation_summary="Perfil de un docente (alumno con inscripcion activa o el mismo docente)",
    )
    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated],
            url_path='profile')
    def profile(self, request, pk=None):
        teacher = get_object_or_404(Teacher.objects.select_related('user'), user_id=pk)

        if not self._can_view_profile(request.user, teacher):
            raise NotFound("Perfil no disponible.")

        return Response(TeacherProfileSerializer(teacher).data)

    def _can_view_profile(self, user, teacher):
        if getattr(user, 'is_teacher', False) and user.pk == teacher.pk:
            return True
        if getattr(user, 'is_student', False):
            teacher_commissions = Commission.objects.filter(
                Q(chief_teacher=teacher) | Q(teachers=teacher)
            )
            return CommissionInscription.objects.filter(
                student__user=user,
                status='A',
                semester__start_date__year=get_current_year(),
                semester__year_moment=get_current_semester(),
                semester__commission__in=teacher_commissions,
            ).exists()
        return False
