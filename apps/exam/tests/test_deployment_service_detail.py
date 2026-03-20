from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from apps.exam.core.exceptions import DeploymentForbiddenError, DeploymentGoneError
from apps.exam.services.exam_deployment_services import ExamDeploymentService


class ExamDeploymentServiceDetailTests(SimpleTestCase):
    def test_raises_403_when_session_is_not_verified(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace()

        with (
            patch.object(
                ExamDeploymentService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch.object(
                ExamDeploymentService,
                "_ensure_user_can_view_exam",
                return_value=None,
            ),
        ):
            with self.assertRaisesMessage(DeploymentForbiddenError, "권한이 없습니다."):
                ExamDeploymentService.get_deployment_detail(
                    user_id=1,
                    deployment_id=10,
                    verified=False,
                )

    def test_raises_410_when_exam_is_closed(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace()

        with (
            patch.object(
                ExamDeploymentService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch.object(
                ExamDeploymentService,
                "_ensure_user_can_view_exam",
                return_value=None,
            ),
            patch.object(
                ExamDeploymentService,
                "_is_deployment_closed",
                return_value=True,
            ),
        ):
            with self.assertRaisesMessage(DeploymentGoneError, "시험이 종료되었습니다."):
                ExamDeploymentService.get_deployment_detail(
                    user_id=1,
                    deployment_id=10,
                    verified=True,
                )

    def test_returns_detail_response_when_request_is_valid(self) -> None:
        user = SimpleNamespace(id=1)
        exam = SimpleNamespace(id=100, title="TypeScript 기본 문법 테스트")
        deployment = SimpleNamespace(
            exam=exam,
            duration_time=30,
            questions_snapshot_json=[
                {
                    "question_id": 1,
                    "number": 1,
                    "type": "single_choice",
                    "question": "문제 1",
                    "point": 10,
                    "prompt": None,
                    "blank_count": None,
                    "options": ["A", "B", "C"],
                },
                {
                    "question_id": 2,
                    "number": 2,
                    "type": "fill_blank",
                    "question": "문제 2",
                    "point": 20,
                    "prompt": "빈칸 채우기",
                    "blank_count": 2,
                    "options": None,
                },
            ],
        )
        submission = SimpleNamespace(
            cheating_count=1,
            started_at=timezone.now() - timedelta(minutes=5),
            submitted_at=None,
            answers_json={
                "answers": [
                    {"question_id": 1, "submitted_answer": "A"},
                ]
            },
        )

        with (
            patch.object(
                ExamDeploymentService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch.object(
                ExamDeploymentService,
                "_ensure_user_can_view_exam",
                return_value=None,
            ),
            patch.object(
                ExamDeploymentService,
                "_is_deployment_closed",
                return_value=False,
            ),
            patch.object(
                ExamDeploymentService,
                "_get_submission",
                return_value=submission,
            ),
        ):
            result = ExamDeploymentService.get_deployment_detail(
                user_id=1,
                deployment_id=10,
                verified=True,
            )

        self.assertEqual(result["exam_id"], 100)
        self.assertEqual(result["exam_name"], "TypeScript 기본 문법 테스트")
        self.assertEqual(result["duration_time"], 30)
        self.assertEqual(result["cheating_count"], 1)
        self.assertEqual(len(result["questions"]), 2)
        self.assertEqual(result["questions"][0]["answer_input"], "A")
        self.assertEqual(result["questions"][1]["answer_input"], ["", ""])
