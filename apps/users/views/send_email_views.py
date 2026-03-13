from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.send_email_serializers import EmailSendSerializer
from apps.users.services.send_email_services import SendEmailService


class EmailSendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailSendSerializer
    service = SendEmailService()

    @extend_schema(
        summary="이메일 인증 발송 API",
        description="사용자로부터 이메일을 받아 인증 코드를 발송합니다.",
        tags=["Accounts"],
        examples=[
            OpenApiExample(
                name="인증번호 발급 성공 예시",
                value={"detail": "이메일 인증 코드가 전송되었습니다."},
                response_only=True,
                status_codes=["200"],
            ),
        ],
        responses={
            200: OpenApiResponse(description="인증코드가 발송되었습니다."),
            400: OpenApiResponse(description="필수필드 누락/이메일 형식이 아닙니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        self.service.send_email_code(email)

        return Response({"detail": "이메일 인증 코드가 전송되었습니다."}, status=status.HTTP_200_OK)
