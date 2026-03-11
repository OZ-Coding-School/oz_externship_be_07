from rest_framework import serializers

from apps.users.models import User


class AuthorSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.ReadOnlyField(source='profile_img_url')
    course_name = serializers.CharField(read_only=True, default=None)
    cohort_name = serializers.IntegerField(read_only=True, default=1)

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url", "course_name", "cohort_name"]