from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.user_category_serializer import UserCategorySerializer
from apps.questions.services.user_categories_list_services import (
    QuestionCategoryService,
)
from apps.users.choices import UserRole


# API명세서 102번 유저 카테고리 조회
class UserCategoryListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["user_category"],
        summary="유저 카테고리 목록 조회",
        description="수강생 권한을 가진 유저가 카테고리 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(name="page", description="페이지 번호", required=False, type=int, default=1),
            OpenApiParameter(name="size", description="페이지당 항목 수", required=False, type=int, default=10),
            OpenApiParameter(name="search_keyword", description="검색어", required=False, type=str),
            OpenApiParameter(
                name="category_type", description="카테고리 타입(small, medium, large)", required=False, type=str
            ),
        ],
        responses={200: UserCategorySerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        if not request.user or not request.user.is_authenticated:
            return Response({"error_detail": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user

        # 수강생 이상의 권한
        allowed_roles = [UserRole.STUDENT, UserRole.TA, UserRole.OM, UserRole.LC, UserRole.ADMIN]

        # 수강생 이상 권한은 조회 가능
        if user.role not in allowed_roles:
            raise PermissionDenied("카테고리 조회 권한이 없습니다.")

        # 단순 조회이므로 try-except문 제거
        categories = QuestionCategoryService.get_user_category_list().filter(parent__isnull=True)
        serializer = UserCategorySerializer(categories, many=True)

        return Response({"categories": serializer.data}, status=status.HTTP_200_OK)
