from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.find_password_serializers import PasswordFindSerializer
from apps.users.services.find_password_services import PasswordFindService


class PasswordFindView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="비밀번호 분실 시 재설정",
        tags=["Accounts"],
        request=PasswordFindSerializer,
        responses={
            200: OpenApiExample("성공", value={"detail": "비밀번호 변경 성공."}),
            400: OpenApiExample(
                "에러", value={"error_detail": {"email_token": ["유효하지 않거나 만료된 토큰입니다."]}}
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordFindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["email_token"]
        new_pw = serializer.validated_data["new_password"]

        try:
            PasswordFindService.reset_password_with_token(token, new_pw)

            return Response({"detail": "비밀번호 변경 성공."}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error_detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
