from typing import Any

from django.views import View
from rest_framework import permissions
from rest_framework.request import Request

from apps.users.choices import UserRole


class IsSelfOrReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: View) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.id is not None)

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        # if not request.user.is_authenticated:
        #     return False
        if not request.user or request.user.id is None:
            return False

        user_role = getattr(request.user, "role", None)
        is_staff = user_role in [
            UserRole.TA,
            UserRole.OM,
            UserRole.ADMIN,
            UserRole.LC,
        ]

        return bool(obj.author_id == request.user.id or is_staff)
