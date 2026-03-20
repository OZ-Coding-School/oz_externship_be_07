from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.exam.core.exceptions import DeploymentGoneError, DeploymentInvalidSessionError
from apps.exam.services.exam_deployment_services import ExamDeploymentService


class ExamDeploymentServiceStatusTests(SimpleTestCase):
    def test_raises_400_when_session_is_not_verified(self) -> None:
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
            with self.assertRaisesMessage(DeploymentInvalidSessionError, "유효하지 않은 시험 응시 세션입니다."):
                ExamDeploymentService.get_deployment_status(
                    user_id=1,
                    deployment_id=10,
                    verified=False,
                )

    def test_raises_410_when_submission_already_exists(self) -> None:
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
                "_get_submission",
                return_value=SimpleNamespace(id=1),
            ),
        ):
            with self.assertRaisesMessage(DeploymentGoneError, "시험이 이미 종료되었습니다."):
                ExamDeploymentService.get_deployment_status(
                    user_id=1,
                    deployment_id=10,
                    verified=True,
                )

    def test_returns_closed_status_when_deployment_is_closed(self) -> None:
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
                "_get_submission",
                return_value=None,
            ),
            patch.object(
                ExamDeploymentService,
                "_is_deployment_closed",
                return_value=True,
            ),
        ):
            result = ExamDeploymentService.get_deployment_status(
                user_id=1,
                deployment_id=10,
                verified=True,
            )

        self.assertEqual(
            result,
            {
                "exam_status": "closed",
                "force_submit": True,
            },
        )

    def test_returns_activated_status_when_deployment_is_active(self) -> None:
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
                "_get_submission",
                return_value=None,
            ),
            patch.object(
                ExamDeploymentService,
                "_is_deployment_closed",
                return_value=False,
            ),
        ):
            result = ExamDeploymentService.get_deployment_status(
                user_id=1,
                deployment_id=10,
                verified=True,
            )

        self.assertEqual(
            result,
            {
                "exam_status": "activated",
                "force_submit": False,
            },
        )
