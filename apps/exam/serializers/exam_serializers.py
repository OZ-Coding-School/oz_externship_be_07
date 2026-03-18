from typing import Any

from rest_framework import serializers

from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.subject.models.subject_models import Subject


# 쪽지시험 생성 API 및 수정 API
class ExamCreateUpdateSerializer(serializers.ModelSerializer[Exam]):
    thumbnail_img = serializers.ImageField(write_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img", "thumbnail_img_url"]
        read_only_fields = ["id", "thumbnail_img_url"]


# 쪽지시험 목록조회 API - page, size, total_count는 pagenation에서 제공
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
        return f"/admin/exams/{obj.id}"


# 쪽지시험 상세 조회 API - quesitons
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


# 쪽지시험 상세 조회 API - subject
class ExamSubjectDetailSerializer(serializers.ModelSerializer[Subject]):
    class Meta:
        model = Subject
        fields = ["id", "title"]


# 쪽지시험 상세 조회 API
class ExamDetailSerializer(serializers.ModelSerializer[Exam]):
    subject = ExamSubjectDetailSerializer()
    questions = ExamQuestionDetailSerializer(many=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "questions", "thumbnail_img_url", "created_at", "updated_at"]
