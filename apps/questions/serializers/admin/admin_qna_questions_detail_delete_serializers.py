from rest_framework import serializers


class AdminQuestionDeleteSerializer(serializers.Serializer):  # type: ignore[type-arg]
    question_id = serializers.IntegerField()
    deleted_answer_count = serializers.IntegerField()
    deleted_comment_count = serializers.IntegerField()
