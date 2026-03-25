from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


from django.core.cache import cache


class AccountRecoverySerializer(serializers.Serializer[Any]):
    email_token = serializers.CharField(required=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        token = attrs.get("email_token")

        cache_key = f"email_token:{token}"
        user_email = cache.get(cache_key)

        if not user_email:
            return attrs

        try:
            user = User.objects.get(email=user_email)
            attrs["user"] = user
            attrs["cache_key"] = cache_key
        except User.DoesNotExist:
            pass

        return attrs
