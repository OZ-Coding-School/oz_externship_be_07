from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_categoryserializers import (
    AdminCategorySerializer,
)
from apps.questions.services.admin.questions_admin_category_services import (
    AdminCategoryService,
)

# 어드민 카테고리 등록
class AdminCategoryCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="관리자 카테고리 등록",
        request=AdminCategorySerializer,
        responses={201: AdminCategorySerializer},
        tags=["Admin - Questions"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AdminCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = AdminCategoryService.create_category(validated_data=serializer.validated_data)

        response_serializer = AdminCategorySerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

# 어드민 카테고리 목록 조회
