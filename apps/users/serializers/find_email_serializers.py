import re
from typing import Any

from rest_framework import serializers


class FindEmailSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(required=True, error_messages={"required": "이름을 입력해주세요."})
    phone_number = serializers.CharField(required=True, error_messages={"required": "휴대폰번호를 입력해주세요."})
    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        error_messages={"required": "인증번호를 입력해주세요."},
    )

    def validate_phone_number(self, value: str) -> str:
        cleaned = re.sub(r"[^0-9]", "", value)
        if not re.match(r"^01[016789]\d{7,8}$", cleaned):
            raise serializers.ValidationError("올바른 휴대폰번호 형식이 아닙니다.")
        return cleaned
