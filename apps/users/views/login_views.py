from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.login_serializers import LoginSerializer
from apps.users.services.login_services import LoginService


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="로그인 API",
        tags=["Accounts"],
        description="이메일과 비밀번호로 로그인하고, access_token은 바디로, refresh_token은 쿠키로 받습니다.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="로그인 성공",
                response={
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string", "description": "서비스 이용을 위한 액세스 토큰"},
                    },
                },
            ),
            400: OpenApiResponse(description="잘못된 요청 (이메일/비밀번호 불일치)"),
            403: OpenApiResponse(description="탈퇴 신청 계정 (접근 권한 없음)"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = LoginService()
        try:
            result = service.login_user(serializer.validated_data)

            refresh_token = result.pop("refresh")
            response = Response(result, status=status.HTTP_200_OK)

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,
            )
            return response

        except ValidationError as e:
            error_data = e.detail
            status_code: int = status.HTTP_400_BAD_REQUEST

            if isinstance(error_data, dict) and error_data.get("error_type") == "WITHDRAWN":
                status_code = status.HTTP_403_FORBIDDEN

            return Response(error_data, status=status_code)
