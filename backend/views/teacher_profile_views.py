from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import TeacherProfile
from backend.permissions import IsTeacher
from backend.serializers.teacher_profile_serializer import TeacherProfileSerializer
from backend.views.base_view import BaseViewSet


class TeacherProfileViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeacherProfileSerializer

    @action(detail=False, methods=['GET'])
    def me(self, request):
        profile = get_object_or_404(TeacherProfile, teacher=request.user.teacher)
        serializer = TeacherProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def create_profile(self, request):
        if TeacherProfile.objects.filter(teacher=request.user.teacher).exists():
            return Response(
                {'detail': 'El perfil ya existe. Utilice update_profile para modificarlo.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = TeacherProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user.teacher)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['PUT'])
    def update_profile(self, request):
        profile = get_object_or_404(TeacherProfile, teacher=request.user.teacher)
        serializer = TeacherProfileSerializer(profile, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
