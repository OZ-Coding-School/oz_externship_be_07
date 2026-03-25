from datetime import timedelta
from typing import Any, cast

from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.choices import UserStatus
from apps.users.serializers.profile_serializers import (
    NicknameCheckSerializer,
    ProfileImageSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserWithdrawalSerializer,
)

User = get_user_model()
Permission_EXAMPLE = OpenApiExample("인증 에러", value={"error_detail": "자격 인증이 제공되지 않았습니다"})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="내 정보 조회",
        tags=["Accounts"],
        description="로그인한 사용자의 프로필 정보를 가져옵니다.",
        responses={
            200: UserProfileSerializer,
            401: Permission_EXAMPLE,
        },
    )
    def get(self, request: Request) -> Response:
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="내 정보 수정",
        tags=["Accounts"],
        description="내 정보를 수정합니다.",
        request=UserProfileUpdateSerializer,
        responses={
            200: UserProfileUpdateSerializer,
            400: OpenApiExample("입력 에러", value={"error_detail": {"nickname": ["10글자 이하로 해주세요."]}}),
            401: Permission_EXAMPLE,
            409: OpenApiExample("중복 에러", value={"error_detail": {"nickname": ["중복된 닉네임이 존재합니다."]}}),
        },
    )
    def patch(self, request: Request) -> Response:
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        error_str = str(serializer.errors)
        if "중복된 닉네임" in error_str:
            return Response({"error_detail": serializer.errors}, status=status.HTTP_409_CONFLICT)

        return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="회원 탈퇴",
        tags=["Accounts"],
        description="회원 탈퇴 사유를 기록하고 유저 상태를 비활성화합니다.",
        request=UserWithdrawalSerializer,
        methods=["DELETE"],
        responses={
            204: OpenApiExample("성공", value=None),
            400: OpenApiExample(
                "필드 에러",
                value={"error_detail": {"reason": ["탈퇴 사유는 필수 입력 항목입니다."]}},
            ),
            401: Permission_EXAMPLE,
        },
    )
    def delete(self, request: Request) -> Response:
        serializer = UserWithdrawalSerializer(data=request.data)

        if serializer.is_valid():
            user = cast(Any, request.user)
            serializer.save(user=request.user, due_date=timezone.now().date() + timedelta(days=30))

            user.status = UserStatus.DEACTIVATED
            user.is_active = False
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class NicknameCheckView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NicknameCheckSerializer

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


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileImageSerializer

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
