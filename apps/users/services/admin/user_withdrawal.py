from django.db import transaction
from django.http import Http404

from apps.users.choices import UserStatus
from apps.users.models.models import Withdrawal


def restore_withdrawn_user_by_admin(withdrawal_id: int) -> None:
    """
    어드민이 탈퇴 신청 데이터를 삭제하고 유저를 활성화 상태로 복구합니다.
    """
    try:
        withdrawal = Withdrawal.objects.select_related("user").get(id=withdrawal_id)
    except Withdrawal.DoesNotExist:
        raise Http404("회원탈퇴 정보를 찾을 수 없습니다.")

    user = withdrawal.user

    if not user:
        raise Http404("연결된 사용자 정보를 찾을 수 없습니다.")

    with transaction.atomic():
        user.status = UserStatus.ACTIVATED
        user.is_active = True
        user.save(update_fields=["status", "is_active"])

        withdrawal.delete()
