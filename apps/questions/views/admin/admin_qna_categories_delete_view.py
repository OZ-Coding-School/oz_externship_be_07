from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.models import QuestionCategories
from apps.questions.serializers.admin.admin_qna_category_delete_serializers import (
    AdminCategoryDeleteSerializer,
)
from apps.questions.services.admin.questions_admin_category_delete_services import (
    AdminCategoryDeleteService,
)


class AdminCategoryDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="관리자 카테고리 삭제",
        description="카테고리를 삭제하고 관련 질문을 일반질문 카테고리로 이관합니다.",
        responses={200: AdminCategoryDeleteSerializer},
        tags=["Admin - Questions"],
    )
    def delete(self, request: Request, category_id: int) -> Response:
        target_category = get_object_or_404(QuestionCategories, id=category_id)

        result = AdminCategoryDeleteService.execute_delete(target_category)

        serializer = AdminCategoryDeleteSerializer(result)

        return Response(
            {"success": True, "result": {"data": serializer.data}},
            status=status.HTTP_200_OK,
        )
