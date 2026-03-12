from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer[Any]):
    profile_image_url = serializers.ReadOnlyField(source="profile_img_url")
    course_name = serializers.CharField(read_only=True, default=None)
    cohort_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url", "course_name", "cohort_name"]
