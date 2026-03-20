
from typing import Any
from django.db import transaction

from django.db.shortcuts import get_object_or_404

from apps.exam.models.exam_submission_models import ExamSubmission


class ExamUserSubmissionService:
    @staticmethod
    @transaction.atomic
    def create_submission(user: User, data: Dict[str, Any]) -> ExamSubmission:
        deployment_id = data.get("deployment_id")
        deployment = ExamDeployment.objects.get(id=deployment_id)

        submitted_answers = data.get("answers", [])

        score, correct_count = _calculate_score(
            deployment.questions_snapshot_json,
            submitted_answers
        )

        submission = ExamSubmission.objects.create(
            submitter=user,
            deployment=deployment,
            started_at=data.get("started_at"),
            cheating_count=data.get("cheating_count", 0),
            answers_json=submitted_answers,
            score=score,
            correct_answer_count=correct_count
        )
        return submission

    @staticmethod
    def _calculate_score(snapshot: list[dict[str, Any]], submitted_answers: list[dict[str, Any]]) -> (int, int):
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
        """
        제출 ID로 상세 내역을 조회합니다.
        존재하지 않을 경우 404 에러를 발생시킵니다.
        """
        return get_object_or_404(ExamSubmission, id=submission_id)