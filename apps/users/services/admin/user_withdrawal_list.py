from typing import Any, cast

from django.db.models import Prefetch, QuerySet
from django.http import Http404

from apps.subject.models.cohort_student_models import CohortStudent
from apps.users.choices import UserRole
from apps.users.models.models import Withdrawal

WITHDRAWAL_USER_ROLE_MAP = {
    "user": UserRole.USER,
    "training_assistant": UserRole.TA,
    "operation_manager": UserRole.OM,
    "learning_coach": UserRole.LC,
    "admin": UserRole.ADMIN,
    "student": UserRole.STUDENT,
}


def _assign_courses_to_withdrawal(withdrawal: Withdrawal) -> None:
    if not withdrawal.user:
        setattr(withdrawal, "assigned_courses", [])
        return

    user_with_relation = cast(Any, withdrawal.user)

    courses = [
        {
            "course": {"id": cs.cohort.course.id, "name": cs.cohort.course.name, "tag": cs.cohort.course.tag},
            "cohort": {
                "id": cs.cohort.id,
                "number": cs.cohort.number,
                "status": cs.cohort.status,
                "start_date": cs.cohort.start_date,
                "end_date": cs.cohort.end_date,
            },
        }
        for cs in user_with_relation.cohort_students.all()
    ]
    setattr(withdrawal, "assigned_courses", courses)


def get_withdrawal_list_service(
    search: str | None = None, role: str | None = None, sort: str = "latest"
) -> QuerySet[Withdrawal]:
    queryset = Withdrawal.objects.select_related("user").prefetch_related(
        Prefetch("user__cohort_students", queryset=CohortStudent.objects.select_related("cohort", "cohort__course"))
    )

    if role:
        mapped_role = WITHDRAWAL_USER_ROLE_MAP.get(role.lower())
        if mapped_role:
            queryset = queryset.filter(user__role=mapped_role)

    if search:
        queryset = queryset.filter(user__name__icontains=search)

    order_by = "-created_at" if sort == "latest" else "created_at"
    queryset = queryset.order_by(order_by)

    for withdrawal in queryset:
        _assign_courses_to_withdrawal(withdrawal)

    return queryset


def get_admin_withdrawal_detail_service(withdrawal_id: int) -> Withdrawal:
    try:
        withdrawal = (
            Withdrawal.objects.select_related("user")
            .prefetch_related(
                Prefetch(
                    "user__cohort_students", queryset=CohortStudent.objects.select_related("cohort", "cohort__course")
                )
            )
            .get(id=withdrawal_id)
        )

        _assign_courses_to_withdrawal(withdrawal)
        return withdrawal
    except Withdrawal.DoesNotExist:
        raise Http404("회원탈퇴 정보를 찾을 수 없습니다.")
