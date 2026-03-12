from typing import Any

from rest_framework import serializers


class EmailSendSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "invalid": "올바른 이메일 형식이 아닙니다.",
        },
    )

    def validate_email(self, value: str) -> str:
        return value.strip()
