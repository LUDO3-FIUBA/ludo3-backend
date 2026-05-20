from rest_framework import serializers


class AbsoluteImageField(serializers.ImageField):
    def to_representation(self, value):
        image_url = super().to_representation(value)

        if not image_url or image_url.startswith(('http://', 'https://')):
            return image_url

        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(image_url)

        return image_url