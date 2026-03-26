from typing import Any, cast

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.models import User
from apps.users.serializers.change_password_serializers import PasswordChangeSerializer


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="비밀번호 변경 API",
        tags=["Accounts"],
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiExample("성공", value={"detail": "비밀번호 변경 성공."}),
            400: OpenApiExample("필드 에러", value={"error_detail": {"new_password": ["이 필드는 필수 항목입니다."]}}),
            401: OpenApiExample("인증 에러", value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordChangeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = cast(User, request.user)
        old_pw = serializer.validated_data["old_password"]
        new_pw = serializer.validated_data["new_password"]

        if not user.check_password(old_pw):
            return Response(
                {"error_detail": {"old_password": ["현재 비밀번호가 일치하지 않습니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_pw)
        user.save(update_fields=["password"])

        return Response({"detail": "비밀번호 변경 성공."}, status=status.HTTP_200_OK)
