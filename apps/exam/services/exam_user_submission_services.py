import json
from typing import Any

from django.db import transaction
from rest_framework.exceptions import NotFound

from apps.exam.core.error_custom_base import ConflictException
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.users.models.models import User


class ExamUserSubmissionService:
    @staticmethod
    @transaction.atomic
    def create_submission(user: User, data: dict[str, Any]) -> ExamSubmission:
        deployment_id = data.get("deployment_id", 0)

        if deployment_id and ExamSubmission.objects.filter(submitter=user).filter(deployment_id=deployment_id).exists():
            raise ConflictException(detail="이미 제출된 시험입니다.")

        deployment = ExamDeployment.objects.filter(id=deployment_id).first()
        if not deployment:
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
        if isinstance(snapshot, str):
            snapshot = json.loads(snapshot)

        answer_map = {}

        for ans in submitted_answers:
            q_id = ans.get("question_id")
            if q_id is not None:
                answer_map[int(q_id)] = ans.get("submitted_answer")

        total_score = 0
        correct_count = 0

        for q_info in snapshot:
            raw_q_id = q_info.get("id")
            if raw_q_id is None:
                continue

            q_id = int(raw_q_id)
            correct_val = q_info.get("answer")

            if isinstance(correct_val, str):
                try:
                    correct_val = json.loads(correct_val)
                except (json.JSONDecodeError, ValueError):
                    pass

            submitted_val = answer_map.get(q_id)

            is_correct = False

            if submitted_val == correct_val:
                is_correct = True

            elif isinstance(correct_val, list) and len(correct_val) > 0:
                if submitted_val == correct_val[0]:
                    is_correct = True

            if is_correct:
                total_score += q_info.get("point", 0)
                correct_count += 1

        return total_score, correct_count

    @staticmethod
    def get_submission_detail(submission_id: int) -> ExamSubmission:
        submission = (
            ExamSubmission.objects.select_related(
                "submitter",
                "deployment__exam",
                "deployment__cohort__course",
            )
            .filter(id=submission_id)
            .first()
        )
        if not submission:
            raise NotFound("해당 시험 정보를 찾을 수 없습니다.")

        return submission
