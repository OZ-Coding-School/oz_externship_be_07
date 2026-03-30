from typing import Any

from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models.models import User


class DuplicateUserError(Exception):
    pass


class SignUpService:
    def create_user(self, validated_data: dict[str, Any]) -> User:
        email_token = validated_data.pop("email_token")
        sms_token = validated_data.pop("sms_token")

        email = cache.get(f"email_token:{email_token}")
        if not email:
            raise ValidationError("이메일 인증이 만료되었거나 유효하지 않습니다.")

        phone_number = cache.get(f"sms_token:{sms_token}")
        if not phone_number:
            raise ValidationError("SMS 인증이 만료되었거나 유효하지 않습니다.")

        # 중복 검사
        if User.objects.filter(email=email).exists():
            raise DuplicateUserError()
        if User.objects.filter(phone_number=phone_number).exists():
            raise DuplicateUserError()
        if User.objects.filter(nickname=validated_data.get("nickname")).exists():
            raise DuplicateUserError()

        password = validated_data.pop("password")

        user = User.objects.create_user(
            email=email,
            phone_number=phone_number,
            password=password,
            **validated_data,
        )

        cache.delete(f"email_token:{email_token}")
        cache.delete(f"sms_token:{sms_token}")

        return user


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


class ReTokenService:
    def refresh_access_token(self, refresh_token: str) -> str:
        refresh = RefreshToken(refresh_token)  # type: ignore
        return str(refresh.access_token)
