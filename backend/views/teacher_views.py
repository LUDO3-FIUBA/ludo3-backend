from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.permissions import *
from backend.serializers.teacher_serializer import TeacherSerializer
from backend.views.base_view import BaseViewSet

from ..models import Teacher


class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_teacher or request.user.is_staff


class TeacherViews(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    @swagger_auto_schema(
        tags=["Teachers"],
        operation_summary="Get a list of all teachers"
    )
    def list(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data, status=status.HTTP_201_CREATED)


