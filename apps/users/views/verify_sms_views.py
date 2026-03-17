from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.verify_sms_serializers import SmsVerifySerializer
from apps.users.services.verify_sms_services import VerifySmsService


class SmsVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SmsVerifySerializer
    service = VerifySmsService()
    authentication_classes = []

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
