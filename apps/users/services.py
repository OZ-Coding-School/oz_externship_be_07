from typing import Any, Dict

from django.contrib.auth.hashers import make_password

from .models import User


class UserService:
    def create_user(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop("email_token", None)
        validated_data.pop("sms_token", None)

        password2 = validated_data.pop("hashed_password")
        validated_data["hashed_password"] = make_password(password2)

        return User.objects.create(**validated_data)
