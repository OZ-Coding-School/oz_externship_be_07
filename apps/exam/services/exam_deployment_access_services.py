from __future__ import annotations

from datetime import datetime

from django.core.cache import caches
from django.utils import timezone

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.subject.models.cohort_student_models import CohortStudent
from apps.users.models.models import User


class AccessDeploymentNotFoundError(Exception):
    pass


class AccessDeploymentForbiddenError(Exception):
    pass


class AccessDeploymentLockedError(Exception):
    pass


class AccessUserNotFoundError(Exception):
    pass


class AccessCodeMismatchError(Exception):
    pass


class ExamDeploymentAccessService:
    exam_cache = caches["exam"]

    @staticmethod
    def _get_access_key(*, deployment_id: int, user_id: int) -> str:
        return f"exam:deployment_access:{deployment_id}:user:{user_id}"

    @staticmethod
    def _get_access_ttl_seconds(*, close_at: datetime) -> int:
        ttl = int((close_at - timezone.now()).total_seconds())
        return max(ttl, 1)

    @classmethod
    def is_verified(cls, *, deployment_id: int, user_id: int) -> bool:
        key = cls._get_access_key(
            deployment_id=deployment_id,
            user_id=user_id,
        )
        return bool(cls.exam_cache.get(key) == "verified")

    @staticmethod
    def _get_user_or_raise(*, user_id: int) -> User:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise AccessUserNotFoundError("사용자 정보를 찾을 수 없습니다.") from exc

    @staticmethod
    def _get_deployment_or_raise(*, deployment_id: int) -> ExamDeployment:
        try:
            return ExamDeployment.objects.select_related("cohort").get(pk=deployment_id)
        except ExamDeployment.DoesNotExist as exc:
            raise AccessDeploymentNotFoundError("배포 정보를 찾을 수 없습니다.") from exc

    @classmethod
    def check_deployment_code(cls, *, user_id: int, deployment_id: int, code: str) -> None:
        user = cls._get_user_or_raise(user_id=user_id)
        deployment = cls._get_deployment_or_raise(deployment_id=deployment_id)

        exists = CohortStudent.objects.filter(
            user=user,
            cohort_id=deployment.cohort_id,
        ).exists()
        if not exists:
            raise AccessDeploymentForbiddenError("시험에 응시할 권한이 없습니다.")

        now = timezone.now()
        if now < deployment.open_at:
            raise AccessDeploymentLockedError("아직 응시할 수 없습니다.")

        status = str(deployment.status).upper()
        if status != "ACTIVATED" or now > deployment.close_at:
            raise AccessDeploymentLockedError("아직 응시할 수 없습니다.")

        if deployment.access_code != code:
            raise AccessCodeMismatchError("응시 코드가 일치하지 않습니다.")

        key = cls._get_access_key(
            deployment_id=deployment.id,
            user_id=user.id,
        )
        ttl = cls._get_access_ttl_seconds(close_at=deployment.close_at)
        cls.exam_cache.set(key, "verified", timeout=ttl)