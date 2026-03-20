from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.exam.core.exceptions import (
    DeploymentForbiddenError,
    DeploymentGoneError,
    DeploymentNotFoundError,
    UserNotFoundError,
)
from apps.exam.views.exam_deployment_views import DeploymentDetailAPIView


class DummyUser:
    id: int | None
    is_authenticated: bool

    def __init__(self, user_id: int | None) -> None:
        self.id = user_id
        self.is_authenticated = True


class DeploymentDetailAPIViewTests(SimpleTestCase):
    factory: APIRequestFactory
    user: DummyUser

    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.user = DummyUser(user_id=1)

    def test_returns_200_when_request_is_valid(self) -> None:
        request = self.factory.get("/api/v1/exams/deployments/1")
        force_authenticate(request, user=cast(Any, self.user))

        expected: dict[str, Any] = {
            "exam_id": 1,
            "exam_name": "TypeScript 기본 문법 테스트",
            "duration_time": 30,
            "elapsed_time": 0,
            "cheating_count": 0,
            "questions": [],
        }

        with (
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentAccessService.is_verified",
                return_value=True,
            ) as mock_verified,
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentService.get_deployment_detail",
                return_value=expected,
            ) as mock_service,
        ):
            response = DeploymentDetailAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        mock_verified.assert_called_once_with(deployment_id=1, user_id=1)
        mock_service.assert_called_once_with(user_id=1, deployment_id=1, verified=True)

    def test_returns_403_when_user_has_no_permission(self) -> None:
        request = self.factory.get("/api/v1/exams/deployments/1")
        force_authenticate(request, user=cast(Any, self.user))

        with (
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentAccessService.is_verified",
                return_value=True,
            ),
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentService.get_deployment_detail",
                side_effect=DeploymentForbiddenError("권한이 없습니다."),
            ),
        ):
            response = DeploymentDetailAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_returns_404_when_deployment_does_not_exist(self) -> None:
        request = self.factory.get("/api/v1/exams/deployments/1")
        force_authenticate(request, user=cast(Any, self.user))

        with (
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentAccessService.is_verified",
                return_value=True,
            ),
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentService.get_deployment_detail",
                side_effect=DeploymentNotFoundError("해당 시험 정보를 찾을 수 없습니다."),
            ),
        ):
            response = DeploymentDetailAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "해당 시험 정보를 찾을 수 없습니다.")

    def test_returns_410_when_exam_is_closed(self) -> None:
        request = self.factory.get("/api/v1/exams/deployments/1")
        force_authenticate(request, user=cast(Any, self.user))

        with (
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentAccessService.is_verified",
                return_value=True,
            ),
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentService.get_deployment_detail",
                side_effect=DeploymentGoneError("시험이 종료되었습니다."),
            ),
        ):
            response = DeploymentDetailAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertEqual(response.data["error_detail"], "시험이 종료되었습니다.")

    def test_returns_404_when_user_does_not_exist(self) -> None:
        request = self.factory.get("/api/v1/exams/deployments/1")
        force_authenticate(request, user=cast(Any, self.user))

        with (
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentAccessService.is_verified",
                return_value=True,
            ),
            patch(
                "apps.exam.views.exam_deployment_views.ExamDeploymentService.get_deployment_detail",
                side_effect=UserNotFoundError("사용자 정보를 찾을 수 없습니다."),
            ),
        ):
            response = DeploymentDetailAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "사용자 정보를 찾을 수 없습니다.")
