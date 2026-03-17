from typing import Any

from django.core.validators import RegexValidator
from rest_framework import serializers


class SmsSendSerializer(serializers.Serializer[Any]):
    phone_number = serializers.CharField(
        required=True,
        validators=[RegexValidator(regex=r"^010-?\d{4}-?\d{4}$", message="올바른 휴대폰 번호 형식이 아닙니다.")],
    )

    def validate_phone_number(self, value: str) -> str:
        return value.replace("-", "").strip()
