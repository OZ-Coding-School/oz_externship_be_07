import socket
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
        # 일단 기본 형식 검사(Serializer가 해줌)
        domain = value.split("@")[-1]

        try:
            socket.gethostbyname(domain)
        except socket.gaierror:
            raise serializers.ValidationError("존재하지 않는 이메일 도메인입니다.")

        return value
