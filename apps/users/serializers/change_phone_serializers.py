from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class PhoneNumberChangeSerializer(serializers.Serializer[Dict[str, Any]]):
    phone_verify_token = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value: str) -> str:
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("이미 등록된 휴대폰 번호입니다.")
        return value

    def validate_phone_verify_token(self, value: str) -> str:
        if value == "invalid_token":
            raise serializers.ValidationError("유효하지 않은 토큰입니다.")
        return value
