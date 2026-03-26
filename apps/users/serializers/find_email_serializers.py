import re
from typing import Any

from rest_framework import serializers


class FindEmailSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(required=True, error_messages={"required": "이름을 입력해주세요."})
    sms_token = serializers.CharField(required=True)
