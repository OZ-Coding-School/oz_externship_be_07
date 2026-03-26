from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers

User = get_user_model()


from django.core.cache import cache


class AccountRecoverySerializer(serializers.Serializer[Any]):
    email_token = serializers.CharField(required=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        token = attrs.get("email_token")

        cache_key = f"email_token:{token}"
        user_email = cache.get(cache_key)

        if not user_email:
            raise exceptions.NotFound({"error_detail": "유효하지 않거나 만료된 토큰입니다."})

        try:
            user = User.objects.get(email=user_email)
            attrs["user"] = user
            attrs["cache_key"] = cache_key
        except User.DoesNotExist:
            raise serializers.ValidationError({"error_detail": "해당 토큰과 일치하는 사용자를 찾을 수 없습니다."})

        return attrs
