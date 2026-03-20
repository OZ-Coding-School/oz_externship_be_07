from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.exam.core.exceptions import DeploymentForbiddenError, UserNotFoundError
from apps.exam.views.exam_deployment_views import DeploymentListAPIView


class DummyUser:
    id: int | None
    is_authenticated: bool

    def __init__(self, user_id: int | None) -> None:
        self.id = user_id
        self.is_authenticated = True


class DeploymentListAPIViewTests(SimpleTestCase):
    factory: APIRequestFactory
    user: DummyUser

    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.user = DummyUser(user_id=1)

    def test_returns_200_when_request_is_valid(self) -> None:
        request = self.factory.get("/api/v1/exams/deployments?page=1&status=pending")
        force_authenticate(request, user=cast(Any, self.user))

        expected: dict[str, Any] = {
            "page": 1,
            "has_next": False,
            "results": [],
        }

        with patch(
            "apps.exam.views.exam_deployment_views.ExamDeploymentService.get_user_deployments",
            return_value=expected,
        ) as mock_service:
            response = DeploymentListAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        mock_service.assert_called_once_with(user_id=1, page=1, status="pending")

    def test_returns_403_when_user_has_no_permission(self) -> None:
        request = self.factory.get("/api/v1/exams/deployments")
        force_authenticate(request, user=cast(Any, self.user))

        with patch(
            "apps.exam.views.exam_deployment_views.ExamDeploymentService.get_user_deployments",
            side_effect=DeploymentForbiddenError("권한이 없습니다."),
        ):
            response = DeploymentListAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_returns_404_when_user_does_not_exist(self) -> None:
        request = self.factory.get("/api/v1/exams/deployments")
        force_authenticate(request, user=cast(Any, self.user))

        with patch(
            "apps.exam.views.exam_deployment_views.ExamDeploymentService.get_user_deployments",
            side_effect=UserNotFoundError("사용자 정보를 찾을 수 없습니다."),
        ):
            response = DeploymentListAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "사용자 정보를 찾을 수 없습니다.")
