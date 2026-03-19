from django.shortcuts import get_object_or_404

from apps.users.models.models import User


def delete_user_by_admin(account_id: int) -> int:
    """
    어드민 권한으로 유저를 삭제하고 삭제된 PK를 반환합니다.
    """
    user = get_object_or_404(User, id=account_id)
    user_pk = user.pk
    user.delete()
    return user_pk
