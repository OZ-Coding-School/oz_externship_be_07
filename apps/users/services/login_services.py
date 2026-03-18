from typing import Any

from django.contrib.auth import authenticate
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class LoginService:
    def login_user(self, data: dict[str, str]) -> dict[str, Any]:
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise ValidationError({"error_detail": "이메일 또는 비밀번호가 잘못되었습니다."})

        if hasattr(user, "withdrawals") and user.withdrawals:
            raise ValidationError(
                {
                    "error_type": "WITHDRAWN",
                    "error_detail": "탈퇴 신청한 계정입니다.",
                    "expire_at": user.withdrawals.due_date.strftime("%Y-%m-%d"),
                }
            )

        refresh = RefreshToken.for_user(user)

        return {
            "detail": "로그인 성공",
            "access_token": str(refresh.access_token),
            "refresh": str(refresh),
        }
