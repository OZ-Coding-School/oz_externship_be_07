from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from redis.commands.search.querystring import tags
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.send_sms_serialiers import SmsSendSerializer
from apps.users.services.send_sms_services import SendSmsService


class SmsSendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SmsSendSerializer

    @extend_schema(
        summary="SMS 인증번호 발송 API",
        tags=["Accounts"],
        description="사용자로부터 휴대폰번호를 받아 Twilio를 통해 인증 코드를 발송합니다.",
        examples=[
            OpenApiExample(
                name="인증번호 발급 성공 예시",
                value={"detail": "휴대폰번호 인증 코드가 전송되었습니다."},
                response_only=True,
                status_codes=["200"],
            )
        ],
        responses={
            200: OpenApiResponse(description="인증 코드가 전송 되었습니다."),
            400: OpenApiResponse(description="필수필드 누락/휴대폰 형식이 아닙니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]

        send_sms_service = SendSmsService()
        send_sms_service.send_sms_code(phone_number)

        return Response({"detail": "인증 코드가 전송 되었습니다."}, status=status.HTTP_200_OK)
