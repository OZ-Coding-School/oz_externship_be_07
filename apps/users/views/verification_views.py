from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException, Throttled, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.verification_serializers import (
    EmailSendSerializer,
    EmailVerifySerializer,
    SmsSendSerializer,
    SmsVerifySerializer,
)
from apps.users.services.verification_services import (
    EmailVerifyService,
    SendEmailService,
    SendSmsService,
    VerifySmsService,
)


class EmailSendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailSendSerializer
    service = SendEmailService()
    authentication_classes = []

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


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerifySerializer
    service = EmailVerifyService()
    authentication_classes = []

    @extend_schema(
        summary="이메일 인증 확인 API",
        description="사용자로부터 이메일과 인증 코드를 받아 확인을 완료합니다.",
        tags=["Accounts"],
        examples=[
            OpenApiExample(
                name="인증번호 확인 성공 예시",
                value={"detail": "이메일 인증이 완료되었습니다.", "email_token": "base32word"},
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


class SmsSendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SmsSendSerializer
    sms_service = SendSmsService()

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

        try:
            self.sms_service.send_sms_code(phone_number)
            return Response({"detail": "인증 코드가 전송 되었습니다."}, status=status.HTTP_200_OK)

        except ValueError as e:
            raise Throttled(detail=str(e))

        except Exception as e:
            raise APIException(detail=str(e))


class SmsVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SmsVerifySerializer
    service = VerifySmsService()

    @extend_schema(
        summary="SMS 인증 확인 API",
        description="사용자로부터 휴대폰번호와 인증 코드를 받아 확인을 완료합니다.",
        tags=["Accounts"],
        examples=[
            OpenApiExample(
                name="인증번호 확인 성공 예시",
                value={"detail": "SMS 인증이 완료되었습니다.", "sms_token": "base32word"},
                response_only=True,
                status_codes=["200"],
            ),
        ],
        responses={
            200: OpenApiResponse(description="SMS 인증이 완료되었습니다."),
            400: OpenApiResponse(description="잘못된 인증 코드이거나 만료된 요청입니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        try:
            sms_token = self.service.verify_code(phone_number, code)
            return Response({"detail": "SMS 인증에 성공하였습니다.", "sms_token": sms_token}, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise APIException(detail=str(e))
