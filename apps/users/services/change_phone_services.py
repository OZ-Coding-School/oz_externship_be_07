from typing import Any

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserProfileService:
    @staticmethod
    def change_phone_number(user: Any, token: str) -> str:
        cache_key = f"sms_token:{token}"
        phone_token = cache.get(cache_key)

        if not phone_token:
            raise ValidationError({"code": ["인증 토큰이 유효하지 않거나 만료되었습니다."]})

        if User.objects.filter(phone_number=phone_token).exclude(id=user.id).exists():
            raise ValidationError({"phone_number": ["이미 등록된 휴대폰 번호입니다."]})

        user.phone_number = phone_token
        user.save(update_fields=["phone_number"])

        cache.delete(cache_key)

        return str(phone_token)
