from typing import Any

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.verify_email_serializers import EmailVerifySerializer
from apps.users.services.verify_email_services import EmailVerifyService


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerifySerializer
    service = EmailVerifyService()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = EmailVerifyService()

    @extend_schema(
        summary="이메일 인증 확인 API",
        description="사용자로부터 이메일과 인증 코드를 받아 확인을 완료합니다.",
        tags=["Accounts"],
        examples=[
            OpenApiExample(
                name="인증번호 확인 성공 예시",
                value={"detail": "이메일 인증이 완료되었습니다.", "email_token": "daechungbase32word"},
                response_only=True,
                status_codes=["200"],
            ),
        ],
        responses={
            200: OpenApiResponse(description="이메일 인증이 완료되었습니다."),
            400: OpenApiResponse(description="잘못된 인증 코드이거나 만료된 요청입니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = EmailVerifySerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            email_token = self.service.verify_email_code(email, code)

            return Response(
                {"detail": "이메일 인증에 성공하였습니다.", "email_token": email_token}, status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return Response({"error_detail": {"code": e.detail}}, status=status.HTTP_400_BAD_REQUEST)
