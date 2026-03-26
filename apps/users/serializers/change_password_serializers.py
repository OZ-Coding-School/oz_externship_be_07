from typing import Any

from rest_framework import serializers


class PasswordChangeSerializer(serializers.Serializer[Any]):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        old_pw = attrs.get("old_password")
        new_pw = attrs.get("new_password")

        if old_pw == new_pw:
            raise serializers.ValidationError({"new_password": ["기존 비밀번호와 동일합니다."]})
        return attrs
