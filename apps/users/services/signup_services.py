from typing import Any, Dict

from apps.users.models.models import User


class UserService:
    def create_user(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop("email_token", None)
        validated_data.pop("sms_token", None)

        password = validated_data.pop("password")

        return User.objects.create_user(password=password, **validated_data)
