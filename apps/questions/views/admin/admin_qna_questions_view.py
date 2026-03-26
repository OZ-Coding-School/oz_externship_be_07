from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_questions_serializers import (
    AdminQuestionListResponseSerializer,
)
from apps.questions.services.admin.admin_qna_questions_services import (
    AdminQuestionService,
)


class AdminQuestionListAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="관리자 질의응답 목록 조회",
        description="수강생들이 등록한 질의응답을 목록으로 조회합니다. 검색 및 필터링 기능을 적용할 수 있습니다.",
        parameters=[
            OpenApiParameter(name="page", description="페이지 번호", required=False, type=int, default=1),
            OpenApiParameter(name="size", description="페이지당 항목 수", required=False, type=int, default=20),
            OpenApiParameter(
                name="search_keyword", description="검색어 (제목, 내용, 닉네임)", required=False, type=str
            ),
            OpenApiParameter(name="category_id", description="카테고리 ID", required=False, type=int),
            OpenApiParameter(
                name="answer_status", description="답변 상태 (answered, unanswered)", required=False, type=str
            ),
            OpenApiParameter(
                name="sort", description="정렬 (latest, oldest)", required=False, type=str, default="latest"
            ),
        ],
        responses={200: AdminQuestionListResponseSerializer},
        tags=["Admin - Questions"],
    )
    def get(self, request: Request) -> Response:
        try:
            page = int(request.query_params.get("page", 1))
            size = int(request.query_params.get("size", 20))
        except ValueError:
            page = 1
            size = 20

        search_keyword = request.query_params.get("search_keyword")
        category_id = request.query_params.get("category_id")
        answer_status = request.query_params.get("answer_status")
        sort = request.query_params.get("sort", "latest")

        result = AdminQuestionService.get_question_list(
            page=page,
            size=size,
            search_keyword=search_keyword,
            category_id=int(category_id) if category_id else None,
            answer_status=answer_status,
            sort=sort,
        )

        serializer = AdminQuestionListResponseSerializer(result)

        return Response(serializer.data, status=status.HTTP_200_OK)
