from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class EmailVerifySerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    code = serializers.CharField(
        required=True, min_length=6, max_length=6, error_messages={"required": "6자리 인증번호를 입력해주세요."}
    )

    def validate_code(self, value: str) -> str:
        if not value.isdigit():
            raise ValidationError("인증번호는 숫자만 입력 가능합니다.")

        return value
