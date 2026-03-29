from rest_framework import serializers


class AdminAnswerDeleteSerializer(serializers.Serializer):  # type: ignore[type-arg]
    answer_id = serializers.IntegerField()
    deleted_comment_count = serializers.IntegerField()
