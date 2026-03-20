from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from django.utils import timezone

from apps.exam.core.exceptions import (
    CodeMismatchError,
    DeploymentForbiddenError,
    DeploymentLockedError,
)
from apps.exam.services.exam_deployment_access_services import (
    ExamDeploymentAccessService,
)


class ExamDeploymentAccessServiceTests(SimpleTestCase):
    def test_returns_minimum_ttl_of_one_second(self) -> None:
        close_at = timezone.now() - timedelta(minutes=1)

        result = ExamDeploymentAccessService._get_access_ttl_seconds(close_at=close_at)

        self.assertEqual(result, 1)

    def test_returns_true_when_cache_value_is_verified(self) -> None:
        fake_cache = MagicMock()
        fake_cache.get.return_value = "verified"

        with patch.object(ExamDeploymentAccessService, "exam_cache", new=fake_cache):
            result = ExamDeploymentAccessService.is_verified(deployment_id=1, user_id=2)

        self.assertTrue(result)

    def test_returns_false_when_cache_value_is_not_verified(self) -> None:
        fake_cache = MagicMock()
        fake_cache.get.return_value = None

        with patch.object(ExamDeploymentAccessService, "exam_cache", new=fake_cache):
            result = ExamDeploymentAccessService.is_verified(deployment_id=1, user_id=2)

        self.assertFalse(result)

    def test_raises_403_when_user_is_not_in_cohort(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace(
            id=10,
            cohort_id=3,
            open_at=timezone.now() - timedelta(minutes=10),
            close_at=timezone.now() + timedelta(minutes=10),
            status="ACTIVATED",
            access_code="123456",
        )

        with (
            patch.object(
                ExamDeploymentAccessService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentAccessService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch("apps.exam.services.exam_deployment_access_services.CohortStudent.objects.filter") as mock_filter,
        ):
            mock_filter.return_value.exists.return_value = False

            with self.assertRaisesMessage(DeploymentForbiddenError, "시험에 응시할 권한이 없습니다."):
                ExamDeploymentAccessService.check_deployment_code(
                    user_id=1,
                    deployment_id=10,
                    code="123456",
                )

    def test_raises_423_when_exam_is_not_open_yet(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace(
            id=10,
            cohort_id=3,
            open_at=timezone.now() + timedelta(minutes=10),
            close_at=timezone.now() + timedelta(minutes=20),
            status="ACTIVATED",
            access_code="123456",
        )

        with (
            patch.object(
                ExamDeploymentAccessService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentAccessService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch("apps.exam.services.exam_deployment_access_services.CohortStudent.objects.filter") as mock_filter,
        ):
            mock_filter.return_value.exists.return_value = True

            with self.assertRaisesMessage(DeploymentLockedError, "아직 응시할 수 없습니다."):
                ExamDeploymentAccessService.check_deployment_code(
                    user_id=1,
                    deployment_id=10,
                    code="123456",
                )

    def test_raises_423_when_deployment_is_not_activated(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace(
            id=10,
            cohort_id=3,
            open_at=timezone.now() - timedelta(minutes=10),
            close_at=timezone.now() + timedelta(minutes=20),
            status="INACTIVE",
            access_code="123456",
        )

        with (
            patch.object(
                ExamDeploymentAccessService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentAccessService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch("apps.exam.services.exam_deployment_access_services.CohortStudent.objects.filter") as mock_filter,
        ):
            mock_filter.return_value.exists.return_value = True

            with self.assertRaisesMessage(DeploymentLockedError, "아직 응시할 수 없습니다."):
                ExamDeploymentAccessService.check_deployment_code(
                    user_id=1,
                    deployment_id=10,
                    code="123456",
                )

    def test_raises_423_when_deployment_is_closed(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace(
            id=10,
            cohort_id=3,
            open_at=timezone.now() - timedelta(minutes=20),
            close_at=timezone.now() - timedelta(minutes=1),
            status="ACTIVATED",
            access_code="123456",
        )

        with (
            patch.object(
                ExamDeploymentAccessService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentAccessService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch("apps.exam.services.exam_deployment_access_services.CohortStudent.objects.filter") as mock_filter,
        ):
            mock_filter.return_value.exists.return_value = True

            with self.assertRaisesMessage(DeploymentLockedError, "아직 응시할 수 없습니다."):
                ExamDeploymentAccessService.check_deployment_code(
                    user_id=1,
                    deployment_id=10,
                    code="123456",
                )

    def test_raises_400_when_code_does_not_match(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace(
            id=10,
            cohort_id=3,
            open_at=timezone.now() - timedelta(minutes=10),
            close_at=timezone.now() + timedelta(minutes=20),
            status="ACTIVATED",
            access_code="123456",
        )

        with (
            patch.object(
                ExamDeploymentAccessService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentAccessService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch("apps.exam.services.exam_deployment_access_services.CohortStudent.objects.filter") as mock_filter,
        ):
            mock_filter.return_value.exists.return_value = True

            with self.assertRaisesMessage(CodeMismatchError, "응시 코드가 일치하지 않습니다."):
                ExamDeploymentAccessService.check_deployment_code(
                    user_id=1,
                    deployment_id=10,
                    code="000000",
                )

    def test_sets_verified_cache_when_code_is_valid(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace(
            id=10,
            cohort_id=3,
            open_at=timezone.now() - timedelta(minutes=10),
            close_at=timezone.now() + timedelta(minutes=20),
            status="ACTIVATED",
            access_code="123456",
        )
        fake_cache = MagicMock()

        with (
            patch.object(
                ExamDeploymentAccessService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch.object(
                ExamDeploymentAccessService,
                "_get_deployment_or_raise",
                return_value=deployment,
            ),
            patch("apps.exam.services.exam_deployment_access_services.CohortStudent.objects.filter") as mock_filter,
            patch.object(
                ExamDeploymentAccessService,
                "exam_cache",
                new=fake_cache,
            ),
        ):
            mock_filter.return_value.exists.return_value = True

            ExamDeploymentAccessService.check_deployment_code(
                user_id=1,
                deployment_id=10,
                code="123456",
            )

        fake_cache.set.assert_called_once()
