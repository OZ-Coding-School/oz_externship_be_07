from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.models import QuestionCategories
from apps.questions.services.admin.questions_admin_category_delete_services import (
    AdminCategoryDeleteService,
)


class AdminCategoryDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="관리자 카테고리 삭제",
        description="카테고리를 삭제하고 관련 질문을 일반질문 카테고리로 이관합니다.",
        tags=["Admin_qna"],
        responses={
            200: OpenApiResponse(description="카테고리 삭제 성공"),
            404: OpenApiResponse(description="삭제할 카테고리를 찾을 수 없습니다."),
            409: OpenApiResponse(description="기본 카테고리는 삭제할 수 없습니다."),
        },
    )
    def delete(self, request: Request, category_id: int) -> Response:
        try:
            target_category = QuestionCategories.objects.get(id=category_id)
        except QuestionCategories.DoesNotExist:
            raise NotFound({"error_detail": "삭제할 카테고리를 찾을 수 없습니다."})

        if target_category.name == "일반질문" and target_category.parent is None:
            return Response(
                {"error_detail": "기본 카테고리는 삭제할 수 없습니다."},
                status=status.HTTP_409_CONFLICT,
            )

        result = AdminCategoryDeleteService.execute_delete(target_category)

        return Response(result, status=status.HTTP_200_OK)
