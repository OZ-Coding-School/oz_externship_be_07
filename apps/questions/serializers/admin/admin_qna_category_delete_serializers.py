from rest_framework import serializers


class AdminCategoryDeleteSerializer(serializers.Serializer):  # type: ignore[type-arg]
    category_id = serializers.IntegerField()
    category_type = serializers.CharField()
    migrated_question_count = serializers.IntegerField()
