from rest_framework import serializers

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


# Presigned URL 요청
class PresignedUrlRequestSerializer(serializers.Serializer[None]):
    file_name = serializers.CharField()
