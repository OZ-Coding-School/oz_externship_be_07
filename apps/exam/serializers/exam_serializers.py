from typing import Any

from rest_framework import serializers

from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion


class ExamCreateSerializer(serializers.ModelSerializer[Exam]):
    thumbnail_img = serializers.ImageField(write_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img", "thumbnail_img_url"]
        read_only_fields = ["id", "thumbnail_img_url"]


class ExamListSerializer(serializers.ModelSerializer[Exam]):
    subject_name = serializers.CharField(source="subject.title", read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    submit_count = serializers.IntegerField(read_only=True)
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "subject_name",
            "question_count",
            "submit_count",
            "created_at",
            "updated_at",
            "detail_url",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_detail_url(self, obj: Exam) -> str:
        # 원하는 경로 형식에 맞춰 ID를 조합합니다.
        return f"/admin/exams/{obj.id}"


class ExamQuestionDetailSerializer(serializers.ModelSerializer[ExamQuestion]):
    question_id = serializers.IntegerField(source="id")
    options = serializers.JSONField(source="options_json")
    correct_answer = serializers.JSONField(source="answer")

    class Meta:
        model = ExamQuestion
        fields = [
            "question_id",
            "type",
            "question",
            "prompt",
            "point",
            "options",
            "correct_answer",
            "explanation",
        ]


class ExamDetailSerializer(serializers.ModelSerializer[Exam]):
    subject = serializers.SerializerMethodField()
    questions = ExamQuestionDetailSerializer(source="examquestion_set", many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "questions", "thumbnail_img_url", "created_at", "updated_at"]

    def get_subject(self, obj: Exam) -> dict[str, Any]:
        if not obj.subject:
            return {}
        return {"id": obj.subject.id, "title": obj.subject.title}


class ExamUpdateSerializer(serializers.ModelSerializer[Exam]):
    thumbnail_img = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img", "thumbnail_img_url"]
        read_only_fields = ["id", "thumbnail_img_url"]
