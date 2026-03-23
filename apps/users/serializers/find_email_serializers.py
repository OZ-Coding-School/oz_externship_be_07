import re
from typing import Any

from rest_framework import serializers


class FindEmailSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(required=True, error_messages={"required": "이름을 입력해주세요."})
    phone_number = serializers.CharField(
        required=True,
    )
    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
    )

    def validate_code(self, value: str) -> str:
        if not re.match(r"^\d{6}$", value):
            raise serializers.ValidationError("휴대폰 인증 실패 - 인증코드가 유효하지 않습니다.")
        return value

    def validate_phone_number(self, value: str) -> str:
        return value
