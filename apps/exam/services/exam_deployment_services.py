from __future__ import annotations

import json
from typing import Any

from django.db.models import Exists, OuterRef, QuerySet
from django.utils import timezone

from apps.core.permissions import STAFF_ROLES
from apps.exam.core.exceptions import (
    DeploymentForbiddenError,
    DeploymentGoneError,
    DeploymentInvalidSessionError,
    DeploymentNotFoundError,
    UserNotFoundError,
)
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.cohort_student_models import CohortStudent
from apps.users.models.models import User


class ExamDeploymentService:
    @staticmethod
    def _get_user_or_raise(*, user_id: int) -> User:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise UserNotFoundError("사용자 정보를 찾을 수 없습니다.") from exc

    @staticmethod
    def _get_deployment_or_raise(*, deployment_id: int) -> ExamDeployment:
        try:
            return ExamDeployment.objects.select_related(
                "exam",
                "exam__subject",
                "cohort",
                "cohort__course",
            ).get(pk=deployment_id)
        except ExamDeployment.DoesNotExist as exc:
            raise DeploymentNotFoundError("해당 시험 정보를 찾을 수 없습니다.") from exc

    @classmethod
    def _ensure_user_in_cohort(cls, *, user: User, deployment: ExamDeployment, message: str) -> None:
        if getattr(user, "role", None) in STAFF_ROLES:
            return

        exists = CohortStudent.objects.filter(
            user=user,
            cohort_id=deployment.cohort_id,
        ).exists()

        if not exists:
            raise DeploymentForbiddenError(message)

    @classmethod
    def _ensure_user_can_view_exam(cls, *, user: User, deployment: ExamDeployment) -> None:
        cls._ensure_user_in_cohort(
            user=user,
            deployment=deployment,
            message="권한이 없습니다.",
        )

    @staticmethod
    def _is_deployment_closed(*, deployment: ExamDeployment) -> bool:
        now = timezone.now()
        status = str(deployment.status).upper()
        return status != "ACTIVATED" or now > deployment.close_at

    @staticmethod
    def _extract_snapshot_questions(*, snapshot: Any) -> list[dict[str, Any]]:
        if isinstance(snapshot, dict):
            questions = snapshot.get("questions", [])
            return questions if isinstance(questions, list) else []
        if isinstance(snapshot, list):
            return [item for item in snapshot if isinstance(item, dict)]
        return []

    @staticmethod
    def _parse_options(*, raw_options: Any) -> list[str] | None:
        if raw_options is None:
            return None

        if isinstance(raw_options, list):
            return [str(item) for item in raw_options]

        if isinstance(raw_options, str):
            try:
                parsed = json.loads(raw_options)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                return None

        return None

    @staticmethod
    def _build_answer_map(*, submission: ExamSubmission | None) -> dict[int, Any]:
        if submission is None:
            return {}

        answers_json = submission.answers_json
        answer_map: dict[int, Any] = {}

        if isinstance(answers_json, dict):
            raw_answers = answers_json.get("answers")
            if isinstance(raw_answers, list):
                for item in raw_answers:
                    if not isinstance(item, dict):
                        continue
                    question_id = item.get("question_id")
                    if question_id is None:
                        continue
                    answer_map[int(question_id)] = item.get("submitted_answer")
                return answer_map

        return {}

    @staticmethod
    def _get_default_answer_input(*, question_type: str, blank_count: int | None) -> Any:
        if question_type == "fill_blank":
            return [""] * (blank_count or 0)
        return None

    @staticmethod
    def _get_submission(*, user: User, deployment: ExamDeployment) -> ExamSubmission | None:
        return (
            ExamSubmission.objects.filter(
                submitter=user,
                deployment=deployment,
            )
            .order_by("-id")
            .first()
        )

    @staticmethod
    def _get_elapsed_time(*, submission: ExamSubmission | None) -> int:
        if submission is None or submission.started_at is None:
            return 0

        submitted_at = getattr(submission, "submitted_at", None)
        end_time = submitted_at or timezone.now()

        elapsed_seconds = max(int((end_time - submission.started_at).total_seconds()), 0)
        return elapsed_seconds // 60

    @classmethod
    def get_user_deployments(cls, *, user_id: int, page: int, status: str, page_size: int = 10) -> dict[str, Any]:
        user = cls._get_user_or_raise(user_id=user_id)
        is_staff = getattr(user, "role", None) in STAFF_ROLES

        if not is_staff:
            cohort_ids = list(CohortStudent.objects.filter(user=user).values_list("cohort_id", flat=True))
            if not cohort_ids:
                raise DeploymentForbiddenError("권한이 없습니다.")

        submission_subquery = ExamSubmission.objects.filter(
            submitter=user,
            deployment_id=OuterRef("id"),
        )

        deployments: QuerySet[ExamDeployment] = ExamDeployment.objects.select_related(
            "exam",
            "exam__subject",
        ).annotate(is_done=Exists(submission_subquery))

        if not is_staff:
            deployments = deployments.filter(
                cohort_id__in=cohort_ids,
                status="ACTIVATED",
            )

        deployments = deployments.order_by("-created_at")

        if status == "done":
            deployments = deployments.filter(is_done=True)  # type: ignore[misc]
        elif status == "pending":
            deployments = deployments.filter(is_done=False)  # type: ignore[misc]

        start = (page - 1) * page_size
        end = start + page_size

        paged_deployments = list(deployments[start:end])
        has_next = deployments.count() > end

        deployment_ids = [deployment.id for deployment in paged_deployments]
        submissions = {
            submission.deployment_id: submission
            for submission in ExamSubmission.objects.filter(
                submitter=user,
                deployment_id__in=deployment_ids,
            )
        }

        results: list[dict[str, Any]] = []

        for deployment in paged_deployments:
            submission = submissions.get(deployment.id)
            is_done = submission is not None

            snapshot_questions = cls._extract_snapshot_questions(snapshot=deployment.questions_snapshot_json)
            total_score = sum(int(question.get("point", 0)) for question in snapshot_questions)

            results.append(
                {
                    "id": deployment.id,
                    "submission_id": submission.id if submission else None,
                    "exam": {
                        "id": deployment.exam.id,
                        "title": deployment.exam.title,
                        "thumbnail_img_url": deployment.exam.thumbnail_img_url,
                        "subject": {
                            "id": deployment.exam.subject.id,
                            "title": deployment.exam.subject.title,
                            "thumbnail_img_url": deployment.exam.subject.thumbnail_img_url,
                        },
                    },
                    "question_count": len(snapshot_questions),
                    "total_score": total_score,
                    "exam_info": {
                        "status": "done" if is_done else "pending",
                        "score": submission.score if submission else None,
                        "correct_answer_count": submission.correct_answer_count if submission else None,
                    },
                    "is_done": is_done,
                    "duration_time": deployment.duration_time,
                }
            )

        return {
            "page": page,
            "has_next": has_next,
            "results": results,
        }

    @classmethod
    def get_deployment_detail(cls, *, user_id: int, deployment_id: int, verified: bool) -> dict[str, Any]:
        user = cls._get_user_or_raise(user_id=user_id)
        deployment = cls._get_deployment_or_raise(deployment_id=deployment_id)

        cls._ensure_user_can_view_exam(user=user, deployment=deployment)

        is_staff = getattr(user, "role", None) in STAFF_ROLES
        if not is_staff and not verified:
            raise DeploymentForbiddenError("권한이 없습니다.")

        if cls._is_deployment_closed(deployment=deployment):
            raise DeploymentGoneError("시험이 종료되었습니다.")

        submission = cls._get_submission(user=user, deployment=deployment)
        answer_map = cls._build_answer_map(submission=submission)
        snapshot_questions = cls._extract_snapshot_questions(snapshot=deployment.questions_snapshot_json)

        questions: list[dict[str, Any]] = []

        for index, question in enumerate(snapshot_questions, start=1):
            question_id = int(question.get("question_id", question.get("id", index)))
            question_type = str(question.get("type", "single_choice"))
            blank_count = question.get("blank_count")
            questions.append(
                {
                    "question_id": question_id,
                    "number": int(question.get("number", index)),
                    "type": question_type,
                    "question": str(question.get("question", "")),
                    "point": int(question.get("point", 0)),
                    "prompt": question.get("prompt"),
                    "blank_count": blank_count,
                    "options": cls._parse_options(raw_options=question.get("options", question.get("options_json"))),
                    "answer_input": answer_map.get(
                        question_id,
                        cls._get_default_answer_input(
                            question_type=question_type,
                            blank_count=blank_count if isinstance(blank_count, int) else None,
                        ),
                    ),
                }
            )

        return {
            "exam_id": deployment.exam.id,
            "exam_name": deployment.exam.title,
            "duration_time": deployment.duration_time,
            "elapsed_time": cls._get_elapsed_time(submission=submission),
            "cheating_count": submission.cheating_count if submission else 0,
            "questions": questions,
        }

    @classmethod
    def get_deployment_status(cls, *, user_id: int, deployment_id: int, verified: bool) -> dict[str, Any]:
        user = cls._get_user_or_raise(user_id=user_id)
        deployment = cls._get_deployment_or_raise(deployment_id=deployment_id)

        cls._ensure_user_can_view_exam(user=user, deployment=deployment)

        if not verified:
            raise DeploymentInvalidSessionError("유효하지 않은 시험 응시 세션입니다.")

        submission = cls._get_submission(user=user, deployment=deployment)
        if submission is not None:
            raise DeploymentGoneError("시험이 이미 종료되었습니다.")

        if cls._is_deployment_closed(deployment=deployment):
            return {
                "exam_status": "closed",
                "force_submit": True,
            }

        return {
            "exam_status": "activated",
            "force_submit": False,
        }
