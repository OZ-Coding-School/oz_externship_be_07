import urllib
import urllib.parse
import uuid
from datetime import date
from typing import Any, cast

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.choices import SocialProvider, UserGender
from apps.users.models import SocialUser

User = get_user_model()


class BaseSocialLoginService:
    def __init__(self) -> None:
        self.client_id: str = ""
        self.client_secret: str = ""
        self.redirect_uri: str = ""
        self.token_url: str = ""
        self.user_info_url: str = ""
        self.provider_name: str = ""

    def generate_state(self) -> str:
        return str(uuid.uuid4())

    def generate_unique_nickname(self, prefix: str) -> str:
        last_user = User.objects.filter(nickname__startswith=prefix).order_by("-nickname").first()
        if not last_user:
            return f"{prefix}1"
        try:
            nickname = str(last_user.nickname)
            last_number = int(nickname.split("_")[1])
            return f"{prefix}{last_number + 1}"
        except (IndexError, ValueError):
            return f"{prefix}{uuid.uuid4().hex[:5]}"

    def get_access_token(self, code: str, state: str | None = None) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }
        if state:
            data["state"] = state

        response = requests.post(self.token_url, data=data)
        if not response.ok:
            raise AuthenticationFailed(f"{self.provider_name} 토큰 발급에 실패했습니다.")
        token = response.json().get("access_token")
        return str(token) if token else ""

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.user_info_url, headers=headers)

        if not response.ok:
            raise AuthenticationFailed(f"{self.provider_name} 유저 정보 가져오기에 실패했습니다.")

        return cast(dict[str, Any], response.json())

    def extract_user_data(self, user_info: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def get_or_create_user(self, user_data: dict[str, Any]) -> dict[str, Any]:
        email: str = str(user_data.get("email", ""))
        provider: str = str(user_data.get("provider", ""))
        provider_id: str = str(user_data.get("provider_id", ""))

        social_account = SocialUser.objects.filter(provider=provider, provider_id=provider_id).first()

        if social_account:
            user = social_account.user
        else:
            with transaction.atomic():
                user = User.objects.create(
                    email=email,
                    name=user_data.get("name", ""),
                    nickname=user_data.get("nickname", ""),
                    phone_number=f"010-{str(uuid.uuid4())[:8]}",
                    gender=UserGender.MALE,
                    birthday=date(1900, 1, 1),
                )
                SocialUser.objects.create(user=user, provider=provider, provider_id=provider_id)

        if not user.is_active:
            raise PermissionDenied({"error_detail": {"detail": "탈퇴 신청한 계정입니다.", "expire_at": "2026-03-19"}})

        refresh = RefreshToken.for_user(user)
        return {"access_token": str(refresh.access_token), "refresh_token": str(refresh)}


class KakaoLoginService(BaseSocialLoginService):
    def __init__(self) -> None:
        super().__init__()
        self.client_id = settings.KAKAO_CLIENT_ID or ""
        self.client_secret = settings.KAKAO_CLIENT_SECRET or ""
        self.redirect_uri = settings.KAKAO_REDIRECT_URI or ""
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.user_info_url = "https://kapi.kakao.com/v2/user/me"
        self.provider_name = "카카오"

    def get_access_url(self) -> tuple[str, str]:
        state = self.generate_state()
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
        }
        base_url = "https://kauth.kakao.com/oauth/authorize"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        return url, state

    def extract_user_data(self, user_info: dict[str, Any]) -> dict[str, Any]:
        social_id = str(user_info.get("id"))
        return {
            "email": f"kakao_{social_id}@kakao.com",
            "name": "카카오유저",
            "nickname": self.generate_unique_nickname("K_"),
            "provider": SocialProvider.KAKAO,
            "provider_id": social_id,
        }


class NaverLoginService(BaseSocialLoginService):
    def __init__(self) -> None:
        super().__init__()
        self.client_id = settings.NAVER_CLIENT_ID or ""
        self.client_secret = settings.NAVER_CLIENT_SECRET or ""
        self.redirect_uri = settings.NAVER_REDIRECT_URI or ""
        self.token_url = "https://nid.naver.com/oauth2.0/token"
        self.user_info_url = "https://openapi.naver.com/v1/nid/me"
        self.provider_name = "네이버"

    def get_access_url(self) -> tuple[str, str]:
        state = self.generate_state()
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
        }
        base_url = "https://nid.naver.com/oauth2.0/authorize"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        return url, state

    def extract_user_data(self, user_info: dict[str, Any]) -> dict[str, Any]:
        social_id = str(user_info.get("response", {}).get("id"))
        return {
            "email": f"naver_{social_id[:10]}@naver.com",
            "name": "네이버유저",
            "nickname": self.generate_unique_nickname("N_"),
            "provider": SocialProvider.NAVER,
            "provider_id": social_id,
        }
