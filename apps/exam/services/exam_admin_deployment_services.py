import secrets
import string
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Avg, Count, QuerySet

from apps.exam.core.exceptions import AdminDeploymentDuplicateError
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.cohort_student_models import CohortStudent


class ExamDeploymentService:
    @staticmethod
    def _generate_access_code(length: int = 8) -> str:
        chars = string.digits + string.ascii_letters
        while True:
            code = "".join(secrets.choice(chars) for _ in range(length))
            if not ExamDeployment.objects.filter(access_code=code).exists():
                return code

    @staticmethod
    def _build_questions_snapshot(exam: Exam) -> list[dict[str, Any]]:
        questions = ExamQuestion.objects.filter(exam=exam).order_by("id")
        return [
            {
                "id": question.id,
                "question": question.question,
                "prompt": question.prompt,
                "blank_count": question.blank_count,
                "options_json": question.options_json,
                "type": question.type,
                "answer": question.answer,
                "point": question.point,
                "explanation": question.explanation,
            }
            for question in questions
        ]

    @classmethod
    @transaction.atomic
    def create_deployment(cls, validated_data: dict[str, Any]) -> ExamDeployment:
        exam = validated_data["exam"]
        cohort = validated_data["cohort"]

        if ExamDeployment.objects.filter(exam=exam, cohort=cohort).exists():
            raise AdminDeploymentDuplicateError

        return ExamDeployment.objects.create(
            exam=exam,
            cohort=cohort,
            duration_time=validated_data["duration_time"],
            open_at=validated_data["open_at"],
            close_at=validated_data["close_at"],
            access_code=cls._generate_access_code(),
            questions_snapshot_json=cls._build_questions_snapshot(exam),
        )

    @staticmethod
    def get_list_queryset() -> QuerySet[ExamDeployment]:
        return ExamDeployment.objects.select_related(
            "exam",
            "exam__subject",
            "cohort",
            "cohort__course",
        ).annotate(
            submit_count=Count("examsubmission", distinct=True),
            avg_score=Avg("examsubmission__score"),
        )

    @staticmethod
    def get_detail_queryset() -> QuerySet[ExamDeployment]:
        return ExamDeployment.objects.select_related(
            "exam",
            "exam__subject",
            "cohort",
            "cohort__course",
        )

    @staticmethod
    def get_submit_count(deployment_id: int) -> int:
        return ExamSubmission.objects.filter(deployment_id=deployment_id).count()

    @staticmethod
    def get_total_student_count(cohort_id: int) -> int:
        return CohortStudent.objects.filter(cohort_id=cohort_id).count()

    @staticmethod
    def update_deployment(instance: ExamDeployment, validated_data: dict[str, Any]) -> ExamDeployment:
        for field in ("duration_time", "open_at", "close_at"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save(update_fields=["duration_time", "open_at", "close_at", "updated_at"])
        return instance

    @staticmethod
    def update_status(instance: ExamDeployment, request_status: str) -> ExamDeployment:
        instance.status = request_status.upper()
        instance.save(update_fields=["status", "updated_at"])
        return instance

    @staticmethod
    def delete_deployment(instance: ExamDeployment) -> int:
        deployment_id = instance.id
        instance.delete()
        return deployment_id

    @staticmethod
    def format_datetime(value: Any) -> str:
        return str(value.strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def format_list_status(value: str) -> str:
        return value.capitalize()

    @staticmethod
    def format_status_response(value: str) -> str:
        return value.lower()

    @staticmethod
    def build_exam_access_url(deployment_id: int) -> str:
        base_url = getattr(settings, "EXAM_ACCESS_BASE_URL", "https://exam.site/start")
        return f"{base_url}/{deployment_id}"
