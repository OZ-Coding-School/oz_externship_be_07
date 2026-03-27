from typing import Optional

from django.db.models import QuerySet

from apps.users.models.models import User


class AdminUserSearchService:
    def get_user_list(
        self, search: Optional[str] = None, status: Optional[str] = None, role: Optional[str] = None
    ) -> QuerySet[User]:
        queryset = User.objects.all().order_by("-created_at")

        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(email__icontains=search)

        if status:
            queryset = queryset.filter(status=status)
        if role:
            queryset = queryset.filter(role=role)

        return queryset

    def get_user_detail(self, account_id: int) -> Optional[User]:
        return User.objects.filter(id=account_id).first()
