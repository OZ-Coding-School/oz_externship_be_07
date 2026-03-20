from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.find_email_serializers import FindEmailSerializer
from apps.users.services.find_email_serivces import FindEmailService


class FindEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="이메일 찾기 API",
        tags=["Accounts"],
        description="이름과 핸드폰번호를 입력하고 인증을 통해 일부 가려진 상태의 이메일을 확인합니다.",
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
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            masked_email = FindEmailService.verify_sms_code(
                name=serializer.validated_data["name"],
                phone_number=serializer.validated_data["phone_number"],
                code=serializer.validated_data["code"],
            )

            return Response({"email": masked_email}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error_detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
