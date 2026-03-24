from django.db.models import Q, QuerySet
from django.http import Http404

from apps.users.choices import UserRole
from apps.users.models.models import Withdrawal


def get_withdrawal_list_service(
    search: str | None = None, role: str | None = None, sort: str = "latest"
) -> QuerySet[Withdrawal]:
    queryset = Withdrawal.objects.select_related("user").all()

    if search:
        queryset = queryset.filter(
            Q(user__name__icontains=search) | Q(user__email__icontains=search) | Q(user__nickname__icontains=search)
        )

    if role:
        role_map = {
            "user": UserRole.USER,
            "training_assistant": UserRole.TA,
            "operation_manager": UserRole.OM,
            "learning_coach": UserRole.LC,
            "admin": UserRole.ADMIN,
            "student": UserRole.STUDENT,
        }
        mapped_role = role_map.get(role.lower())
        if mapped_role:
            queryset = queryset.filter(user__role=mapped_role)

    order_by = "-created_at" if sort == "latest" else "created_at"
    return queryset.order_by(order_by)


def get_admin_withdrawal_detail_service(withdrawal_id: int) -> Withdrawal:
    try:
        return Withdrawal.objects.select_related("user").get(id=withdrawal_id)
    except Withdrawal.DoesNotExist:
        raise Http404("회원탈퇴 정보를 찾을 수 없습니다.")
