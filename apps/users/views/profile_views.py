from typing import Any, cast

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.profile_serializers import (
    NicknameCheckSerializer,
    ProfileImageSerializer,
    UserProfileSerializer,
)

User = get_user_model()


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(
        summary="내 정보 조회",
        tags=["Accounts"],
        description="로그인한 사용자의 프로필 정보를 가져옵니다.",
        responses={200: UserProfileSerializer},
    )
    def get(self, request: Request) -> Response:
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="내 정보 수정",
        tags=["Accounts"],
        description="내정보를 수정합니다.",
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiExample("입력 에러", value={"error_detail": {"phone_number": ["형식이 올바르지 않습니다."]}}),
            409: OpenApiExample("중복 에러", value={"error_detail": {"nickname": ["중복된 닉네임이 존재합니다."]}}),
        },
    )
    def patch(self, request: Request) -> Response:
        serializer = self.serializer_class(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            if "profile_img_url" in request.data and len(request.data) == 1:
                return Response(
                    {"detail": "프로필 사진이 등록되었습니다.", "profile_img_url": serializer.data["profile_img_url"]},
                    status=status.HTTP_200_OK,
                )

            return Response(serializer.data, status=status.HTTP_200_OK)

        error_str = str(serializer.errors)
        if "중복된 닉네임" in error_str or "이미 등록된 휴대폰" in error_str:
            return Response({"error_detail": serializer.errors}, status=status.HTTP_409_CONFLICT)

        return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="닉네임 중복 확인",
        tags=["Accounts"],
        description="닉네임이 중복되는지 확인합니다..",
        request=NicknameCheckSerializer,
        responses={
            200: OpenApiExample("성공", value={"detail": "사용가능한 닉네임 입니다."}),
            400: OpenApiExample(
                "필드 누락 ",
                value={"error_detail": {"nickname": ["이 필드는 필수 항목입니다."]}},
            ),
            409: OpenApiExample("중복 에러", value={"error_detail": "중복된 닉네임이 존재합니다."}),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = NicknameCheckSerializer(data=request.data)

        if serializer.is_valid():
            return Response({"detail": "사용가능한 닉네임 입니다."}, status=status.HTTP_200_OK)

        if "중복된 닉네임" in str(serializer.errors):
            return Response({"error_detail": "중복된 닉네임이 존재합니다."}, status=status.HTTP_409_CONFLICT)

        return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="프로필 이미지 수정",
        tags=["Accounts"],
        description="이미지 URL을 받아 사용자의 프로필 사진으로 등록합니다.",
        request=ProfileImageSerializer,
        responses={
            200: ProfileImageSerializer,
            400: OpenApiExample(
                "에러", value={"error_detail": {"profile_img_url": ["올바른 이미지 주소 형식이 아닙니다."]}}
            ),
        },
    )
    def put(self, request: Request) -> Response:
        user = cast(Any, request.user)

        serializer = ProfileImageSerializer(data=request.data)

        if serializer.is_valid():
            user.profile_img_url = serializer.validated_data["profile_img_url"]
            user.save()
            return Response(
                {"detail": "프로필 사진이 등록되었습니다.", "profile_img_url": user.profile_img_url},
                status=status.HTTP_200_OK,
            )

        return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
