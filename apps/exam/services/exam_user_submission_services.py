from typing import Any

from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from apps.exam.core.error_custom_base import ConflictException
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.users.models.models import User


class ExamUserSubmissionService:
    @staticmethod
    @transaction.atomic
    def create_submission(user: User, data: dict[str, Any]) -> ExamSubmission:
        deployment_id = data.get("deployment_id")

        if deployment_id and ExamSubmission.objects.filter(submitter=user).filter(deployment_id=deployment_id).exists():
            raise ConflictException(detail="이미 제출된 시험입니다.")

        try:
            deployment = get_object_or_404(ExamDeployment, id=deployment_id)
        except Http404:
            raise NotFound("해당 시험 정보를 찾을 수 없습니다.")

        submitted_answers = data.get("answers", [])

        score, correct_count = ExamUserSubmissionService._calculate_score(
            deployment.questions_snapshot_json, submitted_answers
        )

        submission = ExamSubmission.objects.create(
            submitter=user,
            deployment=deployment,
            started_at=data.get("started_at", 0),
            cheating_count=data.get("cheating_count", 0),
            answers_json=submitted_answers,
            score=score,
            correct_answer_count=correct_count,
        )
        return submission

    @staticmethod
    def _calculate_score(snapshot: list[dict[str, Any]], submitted_answers: list[dict[str, Any]]) -> tuple[int, int]:
        answer_map = {ans.get("question_id"): ans.get("submitted_answer") for ans in submitted_answers}
        total_score = 0
        correct_count = 0

        for q_info in snapshot:
            q_id = q_info.get("id")
            correct_val = q_info.get("answer")
            submitted_val = answer_map.get(q_id)

            if submitted_val == correct_val:
                total_score += q_info.get("point", 0)
                correct_count += 1

        return total_score, correct_count

    @staticmethod
    def get_submission_detail(submission_id: int) -> ExamSubmission:
        try:
            submission = get_object_or_404(ExamSubmission, id=submission_id)
        except Http404:
            raise NotFound("해당 시험 정보를 찾을 수 없습니다.")
        return submission
