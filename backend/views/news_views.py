import logging
import uuid

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import News
from backend.news_tags import NEWS_TAGS
from backend.permissions import IsAdmin
from backend.serializers.news_serializer import NewsSerializer, NewsWriteSerializer
from backend.services import AwsS3Service
from backend.views.base_view import BaseViewSet

logger = logging.getLogger(__name__)


class NewsViewSet(BaseViewSet):
    queryset = News.objects.select_related('author').all()
    serializer_class = NewsSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @swagger_auto_schema(tags=["News"], operation_summary="List available tags")
    @action(detail=False, methods=['get'], url_path='tags', permission_classes=[IsAuthenticated])
    def tags(self, request):
        return Response(NEWS_TAGS, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["News"], operation_summary="List all news posts")
    def list(self, request, *args, **kwargs):
        news = self.get_queryset()
        return Response(NewsSerializer(news, many=True).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["News"], operation_summary="Get a news post")
    def retrieve(self, request, pk=None, *args, **kwargs):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(NewsSerializer(post).data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["News"], operation_summary="Create a news post", request_body=NewsWriteSerializer)
    def create(self, request, *args, **kwargs):
        serializer = NewsWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        picture = serializer.validated_data.pop('picture', None)
        picture_url = self._upload_picture(picture)
        post = News.objects.create(
            author=request.user,
            picture_url=picture_url,
            **serializer.validated_data,
        )
        return Response(NewsSerializer(post).data, status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["News"], operation_summary="Update a news post", request_body=NewsWriteSerializer)
    def update(self, request, pk=None, *args, **kwargs):
        return self._update(request, pk, partial=False)

    @swagger_auto_schema(tags=["News"], operation_summary="Partial update a news post", request_body=NewsWriteSerializer)
    def partial_update(self, request, pk=None, *args, **kwargs):
        return self._update(request, pk, partial=True)

    @swagger_auto_schema(tags=["News"], operation_summary="Delete a news post")
    def destroy(self, request, pk=None, *args, **kwargs):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, pk, partial):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = NewsWriteSerializer(post, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        picture = serializer.validated_data.pop('picture', None)
        for field, value in serializer.validated_data.items():
            setattr(post, field, value)
        if picture is not None:
            post.picture_url = self._upload_picture(picture)
        post.updated_at = timezone.now()
        post.save()
        return Response(NewsSerializer(post).data, status.HTTP_200_OK)

    def _upload_picture(self, picture):
        if not picture:
            return ''
        ext = (picture.name.rsplit('.', 1)[-1] if '.' in picture.name else 'jpg').lower()
        file_name = f"news/{uuid.uuid4()}.{ext}"
        try:
            return AwsS3Service().upload_object(picture, file_name)
        except Exception:
            logger.exception("S3 upload failed for news picture")
            return ''
