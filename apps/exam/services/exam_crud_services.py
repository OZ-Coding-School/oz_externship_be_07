from typing import Any

from django.db.models import Count, QuerySet
from django.shortcuts import get_object_or_404

from apps.exam.models.exam_models import Exam
from apps.subject.models.subject_models import Subject


class ExamService:

    # 쪽지시험 생성
    @staticmethod
    def create_exam(data: dict[str, Any]) -> Exam:
        subject_data = data.pop("subject")
        subject_id = subject_data["id"]
        subject = get_object_or_404(Subject, id=subject_id)
        return Exam.objects.create(subject=subject, **data)

    # 쪽지시험 목록조회
    @staticmethod
    def get_exam_queryset(params: dict[str, Any]) -> QuerySet[Exam]:
        queryset = Exam.objects.select_related("subject").annotate(
            question_count=Count("examquestion", distinct=True),
            submit_count=Count("id", distinct=True),  # 실제 운영 시 제출 모델 연결
        )

        search_keyword = params.get("search_keyword")
        if search_keyword:
            queryset = queryset.filter(title__icontains=search_keyword)

        subject_id = params.get("subject_id")
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        sort_field = params.get("sort", "created_at")
        order = params.get("order", "desc")
        order_prefix = "-" if order == "desc" else ""

        allowed_sorts = ["id", "title", "created_at", "updated_at", "question_count"]
        if sort_field not in allowed_sorts:
            sort_field = "created_at"

        queryset = queryset.order_by(f"{order_prefix}{sort_field}")

        return queryset

    # 쪽지시험 상세조회
    @staticmethod
    def get_exam_detail(exam_id: int) -> Exam:
        return get_object_or_404(
            Exam.objects.select_related("subject").prefetch_related("examquestion_set"), id=exam_id
        )

    # 쪽지시험 수정
    @staticmethod
    def update_exam(exam_id: int, data: dict[str, Any]) -> Exam:
        exam = get_object_or_404(Exam, id=exam_id)

        # subject_id가 포함된 경우 처리
        if "subject" in data:
            subject_data = data.pop("subject")
            subject_id = subject_data["id"]
            exam.subject = get_object_or_404(Subject, id=subject_id)

        # title, thumbnail_img_url(source 매핑됨) 등 나머지 필드 업데이트
        for attr, value in data.items():
            setattr(exam, attr, value)

        exam.save()
        return exam

    # 쪽지시험 삭제
    @staticmethod
    def delete_exam(exam_id: int) -> int:
        exam = get_object_or_404(Exam, id=exam_id)
        exam.delete()
        return exam_id
