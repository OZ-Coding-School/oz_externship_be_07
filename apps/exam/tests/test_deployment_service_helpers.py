from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from django.utils import timezone

from apps.exam.core.exceptions import (
    DeploymentForbiddenError,
    DeploymentNotFoundError,
    UserNotFoundError,
)
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.services.exam_deployment_services import ExamDeploymentService
from apps.users.models.models import User


class ExamDeploymentServiceHelperTests(SimpleTestCase):
    def test_extracts_questions_from_dict_snapshot(self) -> None:
        snapshot = {
            "questions": [
                {"question_id": 1, "question": "Q1"},
                {"question_id": 2, "question": "Q2"},
            ]
        }

        result = ExamDeploymentService._extract_snapshot_questions(snapshot=snapshot)

        self.assertEqual(len(result), 2)

    def test_extracts_questions_from_list_snapshot(self) -> None:
        snapshot = [
            {"question_id": 1, "question": "Q1"},
            {"question_id": 2, "question": "Q2"},
        ]

        result = ExamDeploymentService._extract_snapshot_questions(snapshot=snapshot)

        self.assertEqual(len(result), 2)

    def test_returns_empty_list_for_invalid_snapshot(self) -> None:
        result = ExamDeploymentService._extract_snapshot_questions(snapshot="invalid")

        self.assertEqual(result, [])

    def test_parses_options_from_list(self) -> None:
        result = ExamDeploymentService._parse_options(raw_options=["A", "B"])

        self.assertEqual(result, ["A", "B"])

    def test_parses_options_from_json_string(self) -> None:
        result = ExamDeploymentService._parse_options(raw_options='["A", "B"]')

        self.assertEqual(result, ["A", "B"])

    def test_returns_none_for_invalid_options_string(self) -> None:
        result = ExamDeploymentService._parse_options(raw_options="not-json")

        self.assertIsNone(result)

    def test_builds_answer_map_from_submission(self) -> None:
        submission = SimpleNamespace(
            answers_json={
                "answers": [
                    {"question_id": 1, "submitted_answer": "A"},
                    {"question_id": 2, "submitted_answer": ["X", "Y"]},
                ]
            }
        )

        result = ExamDeploymentService._build_answer_map(submission=cast(Any, submission))

        self.assertEqual(result[1], "A")
        self.assertEqual(result[2], ["X", "Y"])

    def test_returns_empty_answer_map_when_submission_is_none(self) -> None:
        result = ExamDeploymentService._build_answer_map(submission=None)

        self.assertEqual(result, {})

    def test_returns_default_answer_input_for_fill_blank(self) -> None:
        result = ExamDeploymentService._get_default_answer_input(
            question_type="fill_blank",
            blank_count=2,
        )

        self.assertEqual(result, ["", ""])

    def test_returns_none_for_non_fill_blank_default_answer(self) -> None:
        result = ExamDeploymentService._get_default_answer_input(
            question_type="single_choice",
            blank_count=None,
        )

        self.assertIsNone(result)

    def test_returns_true_when_deployment_is_closed(self) -> None:
        deployment = SimpleNamespace(
            status="ACTIVATED",
            close_at=timezone.now() - timedelta(minutes=1),
        )

        result = ExamDeploymentService._is_deployment_closed(deployment=cast(Any, deployment))

        self.assertTrue(result)

    def test_returns_false_when_deployment_is_active(self) -> None:
        deployment = SimpleNamespace(
            status="ACTIVATED",
            close_at=timezone.now() + timedelta(minutes=10),
        )

        result = ExamDeploymentService._is_deployment_closed(deployment=cast(Any, deployment))

        self.assertFalse(result)

    def test_returns_zero_elapsed_time_when_submission_is_none(self) -> None:
        result = ExamDeploymentService._get_elapsed_time(submission=None)

        self.assertEqual(result, 0)

    def test_returns_elapsed_minutes_when_submission_exists(self) -> None:
        submission = SimpleNamespace(
            started_at=timezone.now() - timedelta(minutes=5, seconds=10),
            submitted_at=None,
        )

        result = ExamDeploymentService._get_elapsed_time(submission=cast(Any, submission))

        self.assertEqual(result, 5)

    def test_raises_user_not_found_error_when_user_does_not_exist(self) -> None:
        with patch(
            "apps.exam.services.exam_deployment_services.User.objects.get",
            side_effect=User.DoesNotExist,
        ):
            with self.assertRaisesMessage(UserNotFoundError, "사용자 정보를 찾을 수 없습니다."):
                ExamDeploymentService._get_user_or_raise(user_id=1)

    def test_raises_deployment_not_found_error_when_deployment_does_not_exist(self) -> None:
        select_related_mock = MagicMock()
        select_related_mock.get.side_effect = ExamDeployment.DoesNotExist

        with patch(
            "apps.exam.services.exam_deployment_services.ExamDeployment.objects.select_related",
            return_value=select_related_mock,
        ):
            with self.assertRaisesMessage(DeploymentNotFoundError, "해당 시험 정보를 찾을 수 없습니다."):
                ExamDeploymentService._get_deployment_or_raise(deployment_id=1)

    def test_raises_forbidden_error_when_user_is_not_in_cohort(self) -> None:
        user = SimpleNamespace(id=1)
        deployment = SimpleNamespace(cohort_id=10)

        with patch("apps.exam.services.exam_deployment_services.CohortStudent.objects.filter") as mock_filter:
            mock_filter.return_value.exists.return_value = False

            with self.assertRaisesMessage(DeploymentForbiddenError, "권한이 없습니다."):
                ExamDeploymentService._ensure_user_in_cohort(
                    user=cast(Any, user),
                    deployment=cast(Any, deployment),
                    message="권한이 없습니다.",
                )

    def test_returns_filtered_done_deployments(self) -> None:
        user = SimpleNamespace(id=1)

        fake_deployment = SimpleNamespace(
            id=101,
            exam=SimpleNamespace(
                id=1,
                title="HTML 기초",
                thumbnail_img_url="default_img_url",
                subject=SimpleNamespace(
                    id=10,
                    title="HTML",
                    thumbnail_img_url="https://cdn.ozcoding/html.png",
                ),
            ),
            questions_snapshot_json={
                "questions": [
                    {"point": 30},
                    {"point": 70},
                ]
            },
            duration_time=20,
        )

        fake_submission = SimpleNamespace(
            id=333,
            deployment_id=101,
            score=80,
            correct_answer_count=8,
        )

        deployments_qs = MagicMock()
        deployments_qs.filter.return_value = deployments_qs
        deployments_qs.order_by.return_value = deployments_qs
        deployments_qs.annotate.return_value = deployments_qs
        deployments_qs.__getitem__.return_value = [fake_deployment]
        deployments_qs.count.return_value = 1

        with (
            patch.object(
                ExamDeploymentService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch("apps.exam.services.exam_deployment_services.CohortStudent.objects.filter") as mock_cohort_filter,
            patch(
                "apps.exam.services.exam_deployment_services.ExamDeployment.objects.select_related",
                return_value=deployments_qs,
            ),
            patch(
                "apps.exam.services.exam_deployment_services.ExamSubmission.objects.filter"
            ) as mock_submission_filter,
        ):
            mock_cohort_filter.return_value.values_list.return_value = [1]
            mock_submission_filter.side_effect = [
                MagicMock(),  # subquery 용
                [fake_submission],  # 실제 submissions 조회
            ]

            result = ExamDeploymentService.get_user_deployments(
                user_id=1,
                page=1,
                status="done",
            )

        self.assertEqual(result["page"], 1)
        self.assertFalse(result["has_next"])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], 101)
        self.assertEqual(result["results"][0]["submission_id"], 333)
        self.assertEqual(result["results"][0]["question_count"], 2)
        self.assertEqual(result["results"][0]["total_score"], 100)
        self.assertEqual(result["results"][0]["exam_info"]["status"], "done")
        self.assertTrue(result["results"][0]["is_done"])

    def test_raises_forbidden_error_when_user_has_no_cohort_in_list_query(self) -> None:
        user = SimpleNamespace(id=1)

        with (
            patch.object(
                ExamDeploymentService,
                "_get_user_or_raise",
                return_value=user,
            ),
            patch("apps.exam.services.exam_deployment_services.CohortStudent.objects.filter") as mock_filter,
        ):
            mock_filter.return_value.values_list.return_value = []

            with self.assertRaisesMessage(DeploymentForbiddenError, "권한이 없습니다."):
                ExamDeploymentService.get_user_deployments(
                    user_id=1,
                    page=1,
                    status="all",
                )
