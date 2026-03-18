from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

from apps.users.services.re_token_services import ReTokenService


class ReTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="JWT 토큰 재발급 API",
        tags=["Accounts"],
        description="쿠키의 refresh_token으로 access_token을 재발급합니다.",
        responses={
            200: OpenApiResponse(
                description="재발급 성공",
                response={
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string", "description": "서비스 이용을 위한 액세스 토큰"},
                    },
                },
            ),
            400: OpenApiResponse(description="error_detail: { refresh_token: [필수 항목 누락] }"),
            403: OpenApiResponse(description="error_detail: { detail: 로그인 세션 만료 }"),
        },
    )
    def post(self, request: Request) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error_detail": {"refresh_token": ["이 필드는 필수 항목입니다."]}}, status=status.HTTP_400_BAD_REQUEST
            )

        service = ReTokenService()
        try:
            access_token = service.refresh_access_token(refresh_token)
            return Response({"access_token": access_token}, status=status.HTTP_200_OK)

        except TokenError:
            return Response(
                {"error_detail": {"detail": "로그인 세션이 만료되었습니다."}}, status=status.HTTP_403_FORBIDDEN
            )
