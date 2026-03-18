from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="로그아웃 API",
        tags=["Accounts"],
        description="브라우저 쿠키에 저장된 refresh_token을 삭제해 로그아웃 처리합니다.",
        responses={
            200: OpenApiResponse(
                description="로그아웃 성공",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string", "description": "로그아웃 되었습니다."},
                    },
                },
            ),
            401: OpenApiResponse(description="인증 실패 (로그인 필요)"),
        },
    )
    def post(self, request: Request) -> Response:
        response = Response(
            {"detail": "성공적으로 로그아웃 되었습니다."},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(key="refresh_token", samesite="Lax")

        return response
