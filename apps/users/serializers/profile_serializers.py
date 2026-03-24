from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class NicknameCheckSerializer(serializers.Serializer[Dict[str, Any]]):
    nickname = serializers.CharField(max_length=10, required=True)

    def validate_nickname(self, value: str) -> str:
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("중복된 닉네임이 존재합니다.")
        return value


class ProfileImageSerializer(serializers.Serializer[Dict[str, Any]]):
    profile_img_url = serializers.URLField(required=True)

    def validate_profile_img_url(self, value: str) -> str:
        if not value.startswith("https://"):
            raise serializers.ValidationError("올바른 이미지 주소 형식이 아닙니다.")
        return value


class UserProfileSerializer(serializers.ModelSerializer[Any]):

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "nickname",
            "phone_number",
            "gender",
            "birthday",
            "profile_img_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "created_at", "updated_at"]
        extra_kwargs: Dict[str, Any] = {
            "phone_number": {"validators": []},
            "nickname": {"validators": []},
        }

    def validate_nickname(self, value: str) -> str:
        instance = self.instance

        if instance and not isinstance(instance, (list, tuple)):
            user_id = getattr(instance, "id", None)
            if user_id and User.objects.filter(nickname=value).exclude(id=user_id).exists():
                raise serializers.ValidationError("중복된 닉네임이 존재합니다.")
        return value

    def validate_phone_number(self, value: str) -> str:
        instance = self.instance

        if value and instance and not isinstance(instance, (list, tuple)):
            user_id = getattr(instance, "id", None)
            if user_id and User.objects.filter(phone_number=value).exclude(id=user_id).exists():
                raise serializers.ValidationError("이미 등록된 휴대폰 번호입니다.")
        return value
