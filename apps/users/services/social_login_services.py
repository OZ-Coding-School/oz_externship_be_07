import urllib.parse
import uuid
from datetime import date
from typing import Any, cast

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from apps.users.choices import UserGender

User = get_user_model()


class KakaoOAuthService:
    AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
    TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

    def get_auth_url(self) -> tuple[str, str]:
        state = uuid.uuid4().hex
        params = {
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "response_type": "code",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}", state

    def get_access_token(self, code: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }

        response = requests.post(self.TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        return cast(str, response.json().get("access_token"))

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.USER_INFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def parse_kakao_birthday(self, kakao_account: dict[str, Any]) -> date | None:
        birthday = kakao_account.get("birthday")
        if not isinstance(birthday, str) or len(birthday) != 4:
            return None
        try:
            return date(2000, int(birthday[:2]), int(birthday[2:]))
        except ValueError:
            return None

    def get_or_create_user(self, user_info: dict[str, Any]) -> Any:
        kakao_account = user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        kakao_id = str(user_info.get("id"))

        email = kakao_account.get("email", f"kakao_{kakao_id}@temporary.com")
        nickname = profile.get("nickname")
        gender = kakao_account.get("gender")
        birthday_date = self.parse_kakao_birthday(kakao_account)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "nickname": nickname[:10] if nickname else f"kakao_{kakao_id[:4]}",
                "phone_number": "",
                "gender": UserGender.FEMALE if gender == "female" else UserGender.MALE,
                "birthday": birthday_date or date(1990, 1, 1),
            },
        )
        return user


class NaverOAuthService:
    AUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
    TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
    USER_INFO_URL = "https://openapi.naver.com/v1/nid/me"

    def get_auth_url(self) -> tuple[str, str]:
        state = uuid.uuid4().hex
        params = {
            "client_id": settings.NAVER_CLIENT_ID,
            "redirect_uri": settings.NAVER_REDIRECT_URI,
            "response_type": "code",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}", state

    def get_access_token(self, code: str, state: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "code": code,
            "state": state,
        }
        response = requests.post(self.TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        return cast(str, response.json().get("access_token"))

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.USER_INFO_URL, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        profile = data.get("response")
        if not profile:
            raise ValidationError({"code": "naver_api_error", "message": "네이버 프로필 응답이 비어있습니다."})
        return cast(dict[str, Any], profile)

    def parse_naver_birthday(self, profile: dict[str, Any]) -> date | None:
        birthday = profile.get("birthday")
        birthyear = profile.get("birthyear")

        if birthday and birthyear:
            try:
                return date(int(birthyear), int(birthday[:2]), int(birthday[3:]))
            except (ValueError, IndexError):
                pass
        return None

    def get_or_create_user(self, user_info: dict[str, Any]) -> Any:
        naver_id = user_info.get("id")
        email = user_info.get("email", f"naver_{naver_id[:10]}@temporary.com")  # type: ignore
        nickname = user_info.get("nickname")
        gender = user_info.get("gender")
        birthday_date = self.parse_naver_birthday(user_info)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "nickname": nickname[:10] if nickname else f"naver_{naver_id[:4]}",  # type: ignore
                "phone_number": "",
                "gender": UserGender.FEMALE if gender == "F" else UserGender.MALE,
                "birthday": birthday_date or date(1990, 1, 1),
            },
        )
        return user
