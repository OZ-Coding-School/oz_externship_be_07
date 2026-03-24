from typing import Any

from rest_framework import serializers

from apps.subject.models.course_models import Course


class CourseListItemSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "tag",
            "thumbnail_img_url",
        )


class CourseCreateRequestSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(max_length=30)
    tag = serializers.CharField(max_length=3)
    description = serializers.CharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    thumbnail_img_url = serializers.CharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
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
        allow_null=True,
        required=False,
    )
    thumbnail_img_url = serializers.CharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )


class CourseUpdateResponseSerializer(serializers.ModelSerializer[Course]):
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


class CourseDeleteResponseSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()
