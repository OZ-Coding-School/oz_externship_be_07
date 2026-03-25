from django.views import View
from rest_framework import permissions
from rest_framework.request import Request


class IsSelfOrReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: View) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.id is not None)
