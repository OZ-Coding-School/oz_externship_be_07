from typing import Any

from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from apps.exam.core.error_custom_base import ConflictException
from apps.exam.models.exam_submission_models import ExamSubmission


class ExamAdminSubmissionService:

    # 쪽지시험 응시 내역 목록 조회
    @staticmethod
    def get_submission_queryset(params: dict[str, Any]) -> QuerySet[ExamSubmission]:
        queryset = ExamSubmission.objects.select_related(
            "submitter",
            "deployment__cohort__course",
            "deployment__exam__subject",
        )

        search_keyword = params.get("search_keyword")
        if search_keyword:
            queryset = queryset.filter(submitter__name__icontains=search_keyword) | queryset.filter(
                submitter__nickname__icontains=search_keyword
            )

        cohort_id = params.get("cohort_id")
        if cohort_id:
            queryset = queryset.filter(deployment__cohort_id=cohort_id)

        exam_id = params.get("exam_id")
        if exam_id:
            queryset = queryset.filter(deployment__exam_id=exam_id)

        sort_field = params.get("sort", "created_at")
        order = params.get("order", "desc")
        order_prefix = "-" if order == "desc" else ""

        allowed_sorts = ["score", "started_at", "finished_at", "created_at"]
        if sort_field not in allowed_sorts:
            sort_field = "created_at"

        # finished_at은 모델의 created_at으로 매핑
        if sort_field == "finished_at":
            sort_field = "created_at"

        queryset = queryset.order_by(f"{order_prefix}{sort_field}")

        return queryset

    # 쪽지시험 응시 내역 상세 조회
    @staticmethod
    def get_submission_detail(submission_id: int) -> ExamSubmission:
        try:
            return get_object_or_404(
                ExamSubmission.objects.select_related(
                    "submitter",
                    "deployment__cohort__course",
                    "deployment__exam__subject",
                ),
                id=submission_id,
            )
        except Http404:
            raise NotFound("해당 응시 내역을 찾을 수 없습니다.")

    # 쪽지시험 응시 내역 삭제
    @staticmethod
    def delete_submission(submission_id: int) -> int:
        try:
            submission = get_object_or_404(ExamSubmission, id=submission_id)
        except Http404:
            raise NotFound("삭제할 응시 내역을 찾을 수 없습니다.")

        try:
            submission.delete()
        except Exception:
            raise ConflictException(detail="응시 내역 삭제 처리 중 충돌이 발생했습니다.")

        return submission_id