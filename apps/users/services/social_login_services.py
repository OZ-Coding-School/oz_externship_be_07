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
        unique_suffix = uuid.uuid4().hex[:6]
        return f"{prefix}{unique_suffix}"

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

        if not token:
            raise AuthenticationFailed(f"{self.provider_name} 응답에 액세스 토큰이 없습니다.")
        return str(token)

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.user_info_url, headers=headers)

        if not response.ok:
            raise AuthenticationFailed(f"{self.provider_name} 유저 정보 가져오기에 실패했습니다.")

        return cast(dict[str, Any], response.json())

    def extract_user_data(self, user_info: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def get_or_create_user(self, user_data: dict[str, Any]) -> dict[str, Any]:
        email: str = user_data.get("email") or ""
        provider: str = user_data.get("provider") or ""
        provider_id: str = user_data.get("provider_id") or ""

        social_account = SocialUser.objects.filter(provider=provider, provider_id=provider_id).first()

        if social_account:
            user = social_account.user
        else:
            with transaction.atomic():
                social_user = User.objects.filter(email=email).first()
                if not social_user:
                    user = User.objects.create(
                        email=email,
                        name=user_data.get("name", "소셜사용자"),
                        nickname=user_data.get("nickname", "임시닉네임"),
                        phone_number=user_data.get("phone_number", f"010{uuid.uuid4().hex[:4]}{uuid.uuid4().hex[:4]}"),
                        gender=user_data.get("gender", UserGender.MALE),
                        birthday=user_data.get("birthday", date(1900, 1, 1)),
                    )
                else:
                    user = social_user
                SocialUser.objects.create(user=user, provider=provider, provider_id=provider_id)

        if not user.is_active:
            withdrawal = getattr(user, "withdrawals", None)
            expire_at = withdrawal.due_date if withdrawal else "확인 불가"
            raise PermissionDenied({"error_detail": {"detail": "탈퇴 신청한 계정입니다.", "expire_at": str(expire_at)}})

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
        kakao_account = user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        social_id = str(user_info.get("id"))

        gender_map = {"male": UserGender.MALE, "female": UserGender.FEMALE}

        return {
            "email": kakao_account.get("email", f"kakao_{social_id}@kakao.com"),
            "name": profile.get("nickname", "카카오유저"),
            "nickname": self.generate_unique_nickname("K_"),
            "gender": gender_map.get(kakao_account.get("gender"), UserGender.MALE),
            "phone_number": kakao_account.get("phone_number", f"010{uuid.uuid4().hex[:4]}{uuid.uuid4().hex[:4]}"),
            "birthday": date(1995, 1, 1),
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
        naver_response = user_info.get("response", {})
        social_id = str(naver_response.get("id"))

        gender_map = {"M": UserGender.MALE, "F": UserGender.FEMALE}

        return {
            "email": naver_response.get("email", f"naver_{social_id[:10]}@naver.com"),
            "name": naver_response.get("name", "네이버유저"),
            "nickname": self.generate_unique_nickname("N_"),
            "gender": gender_map.get(naver_response.get("gender"), UserGender.MALE),
            "phone_number": naver_response.get("mobile", f"010{uuid.uuid4().hex[:4]}{uuid.uuid4().hex[:4]}"),
            "birthday": date(1995, 1, 1),
            "provider": SocialProvider.NAVER,
            "provider_id": social_id,
        }
