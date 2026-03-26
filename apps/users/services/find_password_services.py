from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.exceptions import ValidationError

User = get_user_model()


class PasswordFindService:
    @staticmethod
    def reset_password_with_token(token: str, new_pw: str) -> None:
        cache_key = f"email_token:{token}"
        user_email = cache.get(cache_key)

        if not user_email:
            raise ValidationError({"email_token": ["유효하지 않거나 만료된 토큰입니다."]})

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise ValidationError({"email_token": ["해당 사용자를 찾을 수 없습니다."]})

        user.set_password(new_pw)
        user.save(update_fields=["password"])

        cache.delete(cache_key)
