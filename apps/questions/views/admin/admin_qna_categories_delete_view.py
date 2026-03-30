from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
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
        description="특정 카테고리를 삭제하며, 해당 카테고리에 속했던 질문들은 자동으로 상위 혹은 기본 카테고리로 이관됩니다.",
        responses={
            200: AdminCategoryDeleteSerializer,
            400: OpenApiResponse(
                description="잘못된 요청",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청 예시",
                        value={"error_detail": "유효하지 않은 카테고리 삭제 요청입니다."},
                    )
                ],
            ),
            401: OpenApiResponse(
                description="인증 실패",
                examples=[
                    OpenApiExample(
                        "로그인 필요 예시",
                        value={"error_detail": "로그인이 필요합니다."},
                    )
                ],
            ),
            403: OpenApiResponse(
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 부족 예시",
                        value={"error_detail": "카테고리 삭제 권한이 없습니다."},
                    )
                ],
            ),
            404: OpenApiResponse(
                description="카테고리 없음",
                examples=[
                    OpenApiExample(
                        "대상 미존재 예시",
                        value={"error_detail": "해당 카테고리를 찾을 수 없습니다."},
                    )
                ],
            ),
            409: OpenApiResponse(
                description="삭제 불가 (기본 카테고리)",
                examples=[
                    OpenApiExample(
                        "기본 카테고리 삭제 시도 예시",
                        value={"error_detail": "기본 카테고리는 삭제할 수 없습니다."},
                    )
                ],
            ),
        },
        tags=["Admin_qna"],
    )
    def delete(self, request: Request, category_id: int) -> Response:
        if category_id <= 0:
            return Response(
                {"error_detail": "유효하지 않은 카테고리 삭제 요청입니다."},  #
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target_category = QuestionCategories.objects.get(id=category_id)
        except QuestionCategories.DoesNotExist:
            return Response(
                {"error_detail": "해당 카테고리를 찾을 수 없습니다."},  #
                status=status.HTTP_404_NOT_FOUND,
            )

        if target_category.name == "일반질문" and target_category.parent is None:
            return Response(
                {"error_detail": "기본 카테고리는 삭제할 수 없습니다."},  #
                status=status.HTTP_409_CONFLICT,
            )

        result = AdminCategoryDeleteService.execute_delete(target_category)
        serializer = AdminCategoryDeleteSerializer(result)

        return Response(serializer.data, status=status.HTTP_200_OK)
