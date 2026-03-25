from django.contrib.auth import get_user_model
from django.core.cache import cache
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.choices import UserStatus
from apps.users.models.models import Withdrawal
from apps.users.serializers.account_recovery_serializers import (
    AccountRecoverySerializer,
)

User = get_user_model()


class AccountRecoveryView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="계정 복구 API",
        tags=["Accounts"],
        request=AccountRecoverySerializer,
        responses={
            200: OpenApiExample("성공", value={"detail": "계정복구가 완료되었습니다."}),
            400: OpenApiExample("필드 에러", value={"error_detail": {"email_token": ["이 필드는 필수 항목입니다."]}}),
            404: OpenApiExample("찾을 수 없음", value={"error_detail": "유효하지 않은 토큰입니다."}),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = AccountRecoverySerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data.get("user")
        cache_key = serializer.validated_data.get("cache_key")

        if not user:
            return Response({"error_detail": "유효하지 않거나 만료된 토큰입니다."}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.status = UserStatus.ACTIVATED
        user.save()

        cache.delete(cache_key)
        Withdrawal.objects.filter(user=user).delete()

        return Response({"detail": "계정복구가 완료되었습니다."}, status=status.HTTP_200_OK)
