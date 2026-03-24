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
from apps.questions.services.user_categories_list_services import QuestionCategoryService


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
        user = request.user
        # 권한 조회
        if not user or user.is_anonymous:
            return Response({"error_detail": "조회권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            categories = QuestionCategoryService.get_user_category_list().filter(parent__isnull=True)
            serializer = UserCategorySerializer(categories, many=True)
            return Response({"categories": serializer.data}, status=status.HTTP_200_OK)

        except ValidationError:
            return Response({"error_detail": "유효하지 않은 카테고리 조회입니다."}, status=status.HTTP_400_BAD_REQUEST)
