from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from backend.models import News
from backend.models.department import Department
from backend.news_tags import NEWS_TAGS
from backend.permissions import get_admin_department_id
from backend.serializers.news_serializer import NewsSerializer, NewsWriteSerializer
from backend.views.base_view import BaseViewSet


class CanPublishNews(BasePermission):
    """Super admin o dept admin (no bedelía, no secretaría)."""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        staff = getattr(user, 'staff', None)
        return bool(staff and staff.department_id and not staff.is_bedelia)


class NewsViewSet(BaseViewSet):
    queryset = News.objects.select_related('author', 'department').all()
    serializer_class = NewsSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), CanPublishNews()]
        return [IsAuthenticated()]

    def _ensure_can_modify(self, request, post):
        """Dept admin solo puede modificar las news de su propio depto. Super: todas."""
        if request.user.is_superuser:
            return
        dept_id = get_admin_department_id(request.user)
        if dept_id is None or post.department_id != dept_id:
            raise PermissionDenied("Solo podés modificar novedades de tu departamento.")

    def _resolve_target_department(self, request, requested_department_id):
        if request.user.is_superuser:
            return requested_department_id
        # Dept admin: siempre su propio depto, ignora cualquier override.
        return get_admin_department_id(request.user)

    @swagger_auto_schema(tags=["News"], operation_summary="List available tags")
    @action(detail=False, methods=['get'], url_path='tags', permission_classes=[IsAuthenticated])
    def tags(self, request):
        return Response(NEWS_TAGS, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["News"], operation_summary="List all news posts")
    def list(self, request, *args, **kwargs):
        news = self.get_queryset()
        return Response(self.get_serializer(news, many=True).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["News"], operation_summary="Get a news post")
    def retrieve(self, request, pk=None, *args, **kwargs):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(self.get_serializer(post).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["News"], operation_summary="Create a news post", request_body=NewsWriteSerializer)
    def create(self, request, *args, **kwargs):
        serializer = NewsWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data.pop('image', None)
        requested_department_id = serializer.validated_data.pop('department_id', None)
        department_id = self._resolve_target_department(request, requested_department_id)

        if department_id is not None and not Department.objects.filter(id=department_id).exists():
            return Response({"department_id": "Departamento inválido."}, status=status.HTTP_400_BAD_REQUEST)

        post = News.objects.create(
            author=request.user,
            image=image,
            department_id=department_id,
            **serializer.validated_data,
        )
        return Response(self.get_serializer(post).data, status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["News"], operation_summary="Update a news post", request_body=NewsWriteSerializer)
    def update(self, request, pk=None, *args, **kwargs):
        return self._update(request, pk, partial=False)

    @swagger_auto_schema(tags=["News"], operation_summary="Partial update a news post", request_body=NewsWriteSerializer)
    def partial_update(self, request, pk=None, *args, **kwargs):
        return self._update(request, pk, partial=True)

    @swagger_auto_schema(tags=["News"], operation_summary="Delete a news post")
    def destroy(self, request, pk=None, *args, **kwargs):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        self._ensure_can_modify(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, pk, partial):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        self._ensure_can_modify(request, post)

        serializer = NewsWriteSerializer(post, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if 'image' in serializer.validated_data:
            post.image = serializer.validated_data['image']

        # department_id solo lo respeta super admin; dept admin queda con su propio depto.
        if 'department_id' in serializer.validated_data:
            requested = serializer.validated_data.pop('department_id')
            if request.user.is_superuser:
                if requested is not None and not Department.objects.filter(id=requested).exists():
                    return Response({"department_id": "Departamento inválido."}, status=status.HTTP_400_BAD_REQUEST)
                post.department_id = requested

        for field, value in serializer.validated_data.items():
            if field == 'image':
                continue
            setattr(post, field, value)

        post.updated_at = timezone.now()
        post.save()
        return Response(self.get_serializer(post).data, status.HTTP_200_OK)
