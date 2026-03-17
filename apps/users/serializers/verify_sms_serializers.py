from typing import Any

from django.core.validators import RegexValidator
from rest_framework import serializers


class SmsVerifySerializer(serializers.Serializer[Any]):
    phone_number = serializers.CharField(
        validators=[RegexValidator(regex=r"^010-?\d{4}-?\d{4}$")],
    )
    code = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate_phone_number(self, value: str) -> str:
        return value.replace("-", "")
