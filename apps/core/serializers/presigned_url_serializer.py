from rest_framework import serializers


# Presigned URL 요청
class PresignedUrlRequestSerializer(serializers.Serializer[None]):
    file_name = serializers.CharField()
