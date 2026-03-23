import urllib.parse
import uuid
from typing import Any

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.services.social_login_services import (
    KakaoOAuthService,
    NaverOAuthService,
)


def frontend_redirect(*, provider: str, is_success: bool = True) -> HttpResponseRedirect:
    base = getattr(settings, "FRONTEND_SOCIAL_REDIRECT_URL", "") or "/"
    params = {"provider": provider, "is_success": str(is_success).lower()}
    return redirect(f"{base}?{urllib.parse.urlencode(params)}")


def set_auth_cookies(resp: HttpResponseRedirect, *, access: str, refresh: str) -> None:
    cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)

    resp.set_cookie(
        "access_token",
        access,
        max_age=3600,
        domain=cookie_domain,
        httponly=False,
        secure=False,
        samesite="Lax",
        path="/",
    )
    resp.set_cookie(
        "refresh_token",
        refresh,
        max_age=604800,
        domain=cookie_domain,
        httponly=True,
        secure=False,
        samesite="Lax",
        path="/",
    )


class KakaoLoginStartView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="카카오 로그인 시작",
        tags=["Accounts"],
        description="**파란색 링크**를 클릭하면 바로 카카오 로그인 화면으로 이동합니다! "
        "**[카카오 로그인 실행하기 (클릭)](/api/v1/accounts/social-login/kakao)",
    )
    def get(self, request: Request) -> Any:
        service = KakaoOAuthService()
        auth_url, state = service.get_auth_url()

        request.session["social_login_state"] = state
        if not request.session.session_key:
            request.session.create()
        request.session.save()

        return redirect(auth_url)


class KakaoLoginCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="카카오 로그인 콜백 (토큰 발급 및 가입)",
        tags=["Accounts"],
        parameters=[
            OpenApiParameter("code", str, description="카카오 인가 코드"),
            OpenApiParameter("state", str, description="보안 상태 값(세션 검증용)"),
        ],
    )
    def get(self, request: Request) -> Any:
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not isinstance(code, str) or not isinstance(state, str):
            return frontend_redirect(provider="kakao", is_success=False)

        saved_state = request.session.get("social_login_state")
        if not saved_state or state != saved_state:
            return frontend_redirect(provider="kakao", is_success=False)

        if "social_login_state" in request.session:
            del request.session["social_login_state"]

        service = KakaoOAuthService()
        try:
            access_token = service.get_access_token(code)
            user_info = service.get_user_info(access_token)
            user = service.get_or_create_user(user_info)

            refresh = RefreshToken.for_user(user)
            response = frontend_redirect(provider="kakao", is_success=True)

            set_auth_cookies(response, access=str(refresh.access_token), refresh=str(refresh))
            return response

        except Exception:
            return frontend_redirect(provider="kakao", is_success=False)


class NaverLoginStartView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="네이버 로그인 시작",
        tags=["Accounts"],
        description="네이버 로그인 화면으로 바로 이동하려면 아래 링크를 클릭하세요."
        "완료 시 자동으로 콜백 처리되어 토큰이 출력됩니다."
        "**[네이버 로그인 실행하기 (클릭)](/api/v1/accounts/social-login/naver)**",
    )
    def get(self, request: Request) -> Any:
        service = NaverOAuthService()
        auth_url, state = service.get_auth_url()

        request.session["social_login_state"] = state
        if not request.session.session_key:
            request.session.create()
        request.session.save()

        return redirect(auth_url)


class NaverLoginCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="네이버 로그인 콜백 (토큰 발급 및 가입)",
        tags=["Accounts"],
        parameters=[
            OpenApiParameter("code", str, description="네이버 인가 코드"),
            OpenApiParameter("state", str, description="보안 상태 값 (세션 검증용)"),
        ],
    )
    def get(self, request: Request) -> Any:
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not isinstance(code, str) or not isinstance(state, str):
            return frontend_redirect(provider="naver", is_success=False)

        saved_state = request.session.get("social_login_state")
        if not saved_state or state != saved_state:
            return frontend_redirect(provider="naver", is_success=False)

        if "social_login_state" in request.session:
            del request.session["social_login_state"]

        service = NaverOAuthService()
        try:
            access_token = service.get_access_token(code, state)
            user_info = service.get_user_info(access_token)
            user = service.get_or_create_user(user_info)

            refresh = RefreshToken.for_user(user)
            response = frontend_redirect(provider="naver", is_success=True)
            set_auth_cookies(response, access=str(refresh.access_token), refresh=str(refresh))
            return response

        except Exception:
            return frontend_redirect(provider="naver", is_success=False)
