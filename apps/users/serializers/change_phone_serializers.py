from typing import Any, Dict

from rest_framework import serializers


class PhoneNumberChangeSerializer(serializers.Serializer[Dict[str, Any]]):
    phone_verify_token = serializers.CharField(required=True)
