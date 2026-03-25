from typing import Any, cast

from django.contrib.auth import get_user_model
from django.core.cache import cache
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.change_phone_serializers import PhoneNumberChangeSerializer
from apps.users.services.change_phone_services import UserProfileService

User = get_user_model()


class ChangePhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="휴대폰 번호 변경",
        tags=["Accounts"],
        description="인증 토큰을 확인하여 사용자의 휴대폰 번호를 변경합니다.",
        request=PhoneNumberChangeSerializer,
        responses={
            200: OpenApiExample(
                "성공", value={"detail": "휴대폰 번호 변경에 성공하였습니다.", "phone_number": "01011112222"}
            ),
            400: OpenApiExample(
                "인증 실패/필드 누락",
                value={"error_detail": {"code": ["휴대폰 인증 실패 - 인증코드가 유효하지 않습니다."]}},
            ),
            401: OpenApiExample("인증 에러", value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}),
            409: OpenApiExample("중복 에러", value={"error_detail": "이미 등록된 휴대폰 번호입니다."}),
        },
    )
    def patch(self, request: Request) -> Response:
        serializer = PhoneNumberChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["phone_verify_token"]

        try:
            new_number = UserProfileService.change_phone_number(request.user, token)

            return Response(
                {"detail": "휴대폰 번호 변경에 성공했습니다.", "phone_number": new_number},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            if "이미 등록된" in str(e.detail):
                return Response({"error_detail": "이미 등록된 휴대폰 번호입니다."}, status=status.HTTP_409_CONFLICT)
            return Response({"error_detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
