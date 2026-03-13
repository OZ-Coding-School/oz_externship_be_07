from typing import Any, Dict

from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from apps.users.models.models import User


class DuplicateUserError(Exception):
    pass


class UserService:
    def create_user(self, validated_data: Dict[str, Any]) -> User:
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
