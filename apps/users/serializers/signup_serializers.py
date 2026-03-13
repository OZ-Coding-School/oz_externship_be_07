from typing import Any, Dict

from rest_framework import serializers


class SignUpSerializer(serializers.Serializer[Dict[str, Any]]):
    password = serializers.CharField(write_only=True)
    nickname = serializers.CharField()
    name = serializers.CharField()
    birthday = serializers.DateField()
    gender = serializers.ChoiceField(choices=["M", "F"])
    email_token = serializers.CharField(write_only=True)
    sms_token = serializers.CharField(write_only=True)
