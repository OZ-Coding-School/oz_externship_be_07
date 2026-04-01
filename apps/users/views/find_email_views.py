from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.find_email_serializers import FindEmailSerializer
from apps.users.services.find_email_services import FindEmailService


class FindEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="이메일 찾기",
        tags=["Accounts"],
        description="이름과 휴대폰인증 후 받은 sms_token을 입력하여 일부 가려진 상태의 이메일을 확인합니다.",
        request=FindEmailSerializer,
        responses={
            200: OpenApiResponse(
                description="이메일을 찾았습니다.",
                response={
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "example": "u**r@e****le.com"},
                    },
                },
            ),
            400: OpenApiResponse(description="잘못된 요청 또는 인증 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = FindEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            masked_email = FindEmailService.find_email(
                name=serializer.validated_data["name"],
                phone_number=serializer.validated_data["phone_number"],
                code=serializer.validated_data["code"],
            )

            return Response({"email": masked_email}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error_detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
