from rest_framework import serializers

from apps.questions.models import Answers, Questions


# 1. 질문 작성자
class AdminQuestionAuthorSerializer(serializers.Serializer):  # type: ignore[type-arg]
    profile_img_url = serializers.CharField(read_only=True)
    nickname = serializers.CharField(read_only=True)
    course_generation = serializers.CharField(read_only=True)

    class Meta:
        ref_name = "AdminQuestionAuthor"


# 2. 답변 작성자
class AdminAnswerAuthorSerializer(serializers.Serializer):  # type: ignore[type-arg]
    profile_img_url = serializers.CharField(read_only=True)
    nickname = serializers.CharField(read_only=True)
    role_title = serializers.CharField(source="role", read_only=True)
    course_generation = serializers.CharField(read_only=True)

    class Meta:
        ref_name = "AdminAnswerAuthor"


# 3. 답변 목록
class AdminAnswerListSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    answer_id = serializers.IntegerField(source="id")
    author = AdminAnswerAuthorSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Answers
        fields = ["answer_id", "author", "content", "is_adopted", "created_at", "updated_at"]
        ref_name = "AdminAnswerList"


# 4. 최종 질문 상세
class AdminQuestionDetailSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    question_id = serializers.IntegerField(source="id")
    images = serializers.SerializerMethodField()
    author = AdminQuestionAuthorSerializer(read_only=True)
    has_answer = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    answers = AdminAnswerListSerializer(many=True, read_only=True)

    class Meta:
        model = Questions
        fields = [
            "question_id",
            "title",
            "content",
            "images",
            "author",
            "view_count",
            "has_answer",
            "created_at",
            "updated_at",
            "answers",
        ]
        ref_name = "AdminQuestionDetail"

    def get_images(self, obj: Questions) -> list[str]:
        return [img.img_url for img in obj.images.all()]

    def get_has_answer(self, obj: Questions) -> bool:
        return bool(obj.answers.all())
