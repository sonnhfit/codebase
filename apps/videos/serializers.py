from rest_framework import serializers


class ImageSerializer(serializers.Serializer):
    img = serializers.CharField(required=True, allow_blank=False)
    user_id = serializers.IntegerField(required=True)
