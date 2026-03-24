from typing import Any

from rest_framework import serializers

from apps.subject.models.course_models import Course


class CourseListItemSerializer(serializers.ModelSerializer[Course]):
    thumbnail_img_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "tag",
            "thumbnail_img_url",
        )

    def get_thumbnail_img_url(self, obj: Course) -> str:
        return obj.thumbnail_img_url or ""


class CourseCreateRequestSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(max_length=30)
    tag = serializers.CharField(max_length=3)
    description = serializers.CharField(
        max_length=255,
        allow_blank=True,
        required=False,
    )
    thumbnail_img_url = serializers.CharField(
        max_length=255,
        allow_blank=True,
        required=False,
    )


class CourseCreateResponseSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()
    id = serializers.IntegerField()


class CourseUpdateRequestSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(max_length=30, required=False)
    tag = serializers.CharField(max_length=3, required=False)
    description = serializers.CharField(
        max_length=255,
        allow_blank=True,
        required=False,
    )
    thumbnail_img_url = serializers.CharField(
        max_length=255,
        allow_blank=True,
        required=False,
    )


class CourseUpdateResponseSerializer(serializers.ModelSerializer[Course]):
    thumbnail_img_url = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "updated_at",
        )

    def get_thumbnail_img_url(self, obj: Course) -> str:
        return obj.thumbnail_img_url or ""

    def get_description(self, obj: Course) -> str:
        return obj.description or ""


class CourseDeleteResponseSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()
