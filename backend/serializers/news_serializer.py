from rest_framework import serializers

from backend.models import News
from backend.news_tags import NEWS_TAGS_BY_KEY


class NewsSerializer(serializers.ModelSerializer):
    tag_label = serializers.SerializerMethodField()
    tag_color = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = (
            'id', 'title', 'description', 'picture_url',
            'tag', 'tag_label', 'tag_color',
            'author', 'author_name',
            'created_at', 'updated_at',
        )
        read_only_fields = fields

    def get_tag_label(self, obj):
        return NEWS_TAGS_BY_KEY.get(obj.tag, {}).get('label', obj.tag)

    def get_tag_color(self, obj):
        return NEWS_TAGS_BY_KEY.get(obj.tag, {}).get('color', '#6b7280')

    def get_author_name(self, obj):
        if not obj.author:
            return None
        full = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return full or obj.author.dni


class NewsWriteSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = News
        fields = ('title', 'description', 'tag', 'picture')
