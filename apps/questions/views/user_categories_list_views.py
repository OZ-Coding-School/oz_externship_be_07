from typing import cast

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.user_category_serializer import UserCategorySerializer
from apps.questions.services.user_categories_list_services import (
    QuestionCategoryService,
)
from apps.users.choices import UserRole
from apps.users.models.models import User


# API명세서 102번 유저 카테고리 조회
class UserCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["user_category"],
        summary="유저 카테고리 목록 조회",
        description="수강생 권한을 가진 유저가 카테고리 목록을 조회합니다.",
        responses={200: UserCategorySerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        user = cast(User, request.user)

        # 수강생 이상의 권한
        allowed_roles = [UserRole.STUDENT, UserRole.TA, UserRole.OM, UserRole.LC, UserRole.ADMIN]

        # 수강생 이상 권한은 조회 가능
        if user.role not in allowed_roles:
            raise PermissionDenied("카테고리 조회 권한이 없습니다.")

        try:
            categories = QuestionCategoryService.get_user_category_list().filter(parent__isnull=True)
            serializer = UserCategorySerializer(categories, many=True)
            return Response({"categories": serializer.data}, status=status.HTTP_200_OK)

        except ValidationError:
            return Response({"error_detail": "유효하지 않은 카테고리 조회입니다."}, status=status.HTTP_400_BAD_REQUEST)
