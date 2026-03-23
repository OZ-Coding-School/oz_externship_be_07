from typing import Any

from django.conf import settings
from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.services.social_login_services import (
    KakaoLoginService,
    NaverLoginService,
)


def generate_social_login_response(login_data: dict[str, Any]) -> Response:
    data = {
        "access_token": login_data["access_token"],
    }
    response = Response(data, status=status.HTTP_200_OK)

    response.set_cookie(
        key="refresh_token",
        value=login_data["refresh_token"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


class KakaoLoginStartView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="카카오 로그인 시작 (인가 페이지 리다이렉트)",
        tags=["Accounts"],
        description="**파란색 링크**를 클릭하면 바로 카카오 로그인 화면으로 이동합니다! "
        "**[카카오 로그인 실행하기 (클릭)](/api/v1/accounts/social-login/kakao)",
    )
    def get(self, request: Any) -> Any:
        service = KakaoLoginService()
        auth_url, state = service.get_access_url()

        request.session["social_login_state"] = state
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
    def get(self, request: Any) -> Response:
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        saved_state = request.session.get("social_login_state")
        if not saved_state or state != saved_state:
            from rest_framework.exceptions import AuthenticationFailed

            raise AuthenticationFailed("잘못된 접근입니다. (보안 위조 위험)")

        del request.session["social_login_state"]

        service = KakaoLoginService()

        access_token = service.get_access_token(code, state)
        user_info = service.get_user_info(access_token)
        user_data = service.extract_user_data(user_info)

        login_data = service.get_or_create_user(user_data)

        return generate_social_login_response(login_data)


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
    def get(self, request: Any) -> Any:
        service = NaverLoginService()
        auth_url, state = service.get_access_url()

        request.session["social_login_state"] = state
        request.session.save()

        return redirect(auth_url)


class NaverLoginCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="네이버 로그인 콜백",
        tags=["Accounts"],
        parameters=[
            OpenApiParameter("code", str, description="네이버 인가 코드"),
            OpenApiParameter("state", str, description="보안 상태 값"),
        ],
    )
    def get(self, request: Any) -> Response:
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        saved_state = request.session.get("social_login_state")
        if not saved_state or state != saved_state:
            from rest_framework.exceptions import AuthenticationFailed

            raise AuthenticationFailed("잘못된 접근입니다. (보안 위조 위험)")

        del request.session["social_login_state"]

        service = NaverLoginService()
        access_token = service.get_access_token(code, state)
        user_info = service.get_user_info(access_token)
        user_data = service.extract_user_data(user_info)

        login_data = service.get_or_create_user(user_data)

        return generate_social_login_response(login_data)
