from typing import Any

from django.utils import timezone
from rest_framework import serializers

from apps.exam.models.exam_models import Exam


# 1. 생성용 (POST)
class ExamCreateSerializer(serializers.ModelSerializer[Exam]):
    thumbnail_img = serializers.ImageField(write_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img", "thumbnail_img_url"]
        read_only_fields = ["id", "thumbnail_img_url"]


# 2. 목록 조회용 (GET List)
class ExamListSerializer(serializers.ModelSerializer[Exam]):
    subject_name = serializers.CharField(source="subject.title", read_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject_name", "created_at", "updated_at"]


# 3. 상세 조회용 (GET Detail)
class ExamDetailSerializer(serializers.ModelSerializer[Exam]):
    subject = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img_url", "created_at", "updated_at"]

    def get_subject(self, obj: Exam) -> dict[str, Any]:
        if not obj.subject:
            return {}
        return {"id": obj.subject.id, "title": obj.subject.title}


# 4. 수정용 (PUT)
class ExamUpdateSerializer(serializers.ModelSerializer[Exam]):
    thumbnail_img = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img", "thumbnail_img_url"]
        read_only_fields = ["id", "thumbnail_img_url"]
