from typing import Any

from django.db.models import Count, QuerySet, ProtectedError
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.exceptions import NotFound

from apps.exam.core.error_custom_base import ConflictException
from apps.exam.models.exam_models import Exam
from apps.subject.models.subject_models import Subject

class ExamService:

    # 쪽지시험 생성
    @staticmethod
    def create_exam(data: dict[str, Any]) -> Exam:
        title = data.get("title")
        if title and Exam.objects.filter(title=title).exists():
            raise ConflictException(detail="동일한 이름의 시험이 이미 존재합니다.")

        subject_data = data.pop("subject")
        subject_id = subject_data.get("id")
        try:
            subject = get_object_or_404(Subject, id=subject_id)
        except Http404:
            raise NotFound("해당 과목 정보를 찾을 수 없습니다.")

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

        try:
            exam = get_object_or_404(Exam, id=exam_id)
        except Http404:
            raise NotFound("수정할 쪽지시험 정보를 찾을 수 없습니다.")

        title = data.get("title")
        if title and Exam.objects.filter(title=title).exclude(id=exam_id).exists():
            raise ConflictException(detail="동일한 이름의 시험이 이미 존재합니다.")

        if "subject" in data:
            subject_data = data.pop("subject")
            subject_id = subject_data.get("id")
            try:
                exam.subject = get_object_or_404(Subject, id=subject_id)
            except Http404:
                raise NotFound("해당 과목 정보를 찾을 수 없습니다.")
        for attr, value in data.items():
            setattr(exam, attr, value)

        exam.save()
        return exam

    # 쪽지시험 삭제
    @staticmethod
    def delete_exam(exam_id: int) -> int:
        try:
            exam = get_object_or_404(Exam, id=exam_id)
        except Http404:
            raise NotFound("삭제하려는 쪽지시험 정보를 찾을 수 없습니다.")

        try:
            exam.delete()
        except ProtectedError:
            raise ConflictException(detail="쪽지시험 삭제 중 충돌이 발생했습니다.")
        except Exception:
            raise ConflictException(detail="쪽지시험 삭제 중 충돌이 발생했습니다.")

        return exam_id
