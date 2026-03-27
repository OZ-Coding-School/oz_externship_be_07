from typing import Any

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LoginService:
    def login_user(self, data: dict[str, str]) -> dict[str, Any]:
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise ValidationError({"error_detail": "이메일과 비밀번호를 모두 입력해주세요."})

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            raise ValidationError({"error_detail": "이메일 또는 비밀번호가 잘못되었습니다."})

        if not user.is_active:
            if hasattr(user, "withdrawals") and user.withdrawals:
                raise ValidationError(
                    {
                        "error_type": "WITHDRAWN",
                        "error_detail": "탈퇴 신청한 계정입니다.",
                        "expire_at": user.withdrawals.due_date.strftime("%Y-%m-%d"),
                    }
                )
            raise ValidationError({"error_type": "WITHDRAWN", "error_detail": "비활성화된 계정입니다."})

        refresh = RefreshToken.for_user(user)

        return {
            "access_token": str(refresh.access_token),
            "refresh": str(refresh),
        }
