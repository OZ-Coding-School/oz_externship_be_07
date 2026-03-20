from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.exam.core.exceptions import (
    CodeMismatchError,
    DeploymentForbiddenError,
    DeploymentLockedError,
    DeploymentNotFoundError,
    UserNotFoundError,
)
from apps.exam.views.exam_deployment_access_views import DeploymentCheckCodeAPIView


class DummyUser:
    id: int | None
    is_authenticated: bool

    def __init__(self, user_id: int | None) -> None:
        self.id = user_id
        self.is_authenticated = True


class DeploymentCheckCodeAPIViewTests(SimpleTestCase):
    factory: APIRequestFactory
    user: DummyUser

    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.user = DummyUser(user_id=1)

    def test_returns_204_when_code_is_valid(self) -> None:
        request = self.factory.post(
            "/api/v1/exams/deployments/1/check-code",
            {"code": "124312"},
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.user))

        with patch(
            "apps.exam.views.exam_deployment_access_views.ExamDeploymentAccessService.check_deployment_code",
            return_value=None,
        ) as mock_service:
            response = DeploymentCheckCodeAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_service.assert_called_once_with(user_id=1, deployment_id=1, code="124312")

    def test_returns_400_when_code_field_is_missing(self) -> None:
        request = self.factory.post(
            "/api/v1/exams/deployments/1/check-code",
            {},
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.user))

        response = DeploymentCheckCodeAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data["error_detail"])

    def test_returns_400_when_code_does_not_match(self) -> None:
        request = self.factory.post(
            "/api/v1/exams/deployments/1/check-code",
            {"code": "wrong"},
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.user))

        with patch(
            "apps.exam.views.exam_deployment_access_views.ExamDeploymentAccessService.check_deployment_code",
            side_effect=CodeMismatchError("응시 코드가 일치하지 않습니다."),
        ):
            response = DeploymentCheckCodeAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "응시 코드가 일치하지 않습니다.")

    def test_returns_403_when_user_has_no_permission(self) -> None:
        request = self.factory.post(
            "/api/v1/exams/deployments/1/check-code",
            {"code": "124312"},
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.user))

        with patch(
            "apps.exam.views.exam_deployment_access_views.ExamDeploymentAccessService.check_deployment_code",
            side_effect=DeploymentForbiddenError("시험에 응시할 권한이 없습니다."),
        ):
            response = DeploymentCheckCodeAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "시험에 응시할 권한이 없습니다.")

    def test_returns_404_when_deployment_does_not_exist(self) -> None:
        request = self.factory.post(
            "/api/v1/exams/deployments/1/check-code",
            {"code": "124312"},
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.user))

        with patch(
            "apps.exam.views.exam_deployment_access_views.ExamDeploymentAccessService.check_deployment_code",
            side_effect=DeploymentNotFoundError("배포 정보를 찾을 수 없습니다."),
        ):
            response = DeploymentCheckCodeAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "배포 정보를 찾을 수 없습니다.")

    def test_returns_423_when_deployment_is_locked(self) -> None:
        request = self.factory.post(
            "/api/v1/exams/deployments/1/check-code",
            {"code": "124312"},
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.user))

        with patch(
            "apps.exam.views.exam_deployment_access_views.ExamDeploymentAccessService.check_deployment_code",
            side_effect=DeploymentLockedError("아직 응시할 수 없습니다."),
        ):
            response = DeploymentCheckCodeAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
        self.assertEqual(response.data["error_detail"], "아직 응시할 수 없습니다.")

    def test_returns_404_when_user_does_not_exist(self) -> None:
        request = self.factory.post(
            "/api/v1/exams/deployments/1/check-code",
            {"code": "124312"},
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.user))

        with patch(
            "apps.exam.views.exam_deployment_access_views.ExamDeploymentAccessService.check_deployment_code",
            side_effect=UserNotFoundError("사용자 정보를 찾을 수 없습니다."),
        ):
            response = DeploymentCheckCodeAPIView.as_view()(request, deployment_id=1)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "사용자 정보를 찾을 수 없습니다.")
