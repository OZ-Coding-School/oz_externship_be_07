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
        parameters=[
            OpenApiParameter(name="page", type=int, default=1),
            OpenApiParameter(name="size", type=int, default=20),
            OpenApiParameter(name="search_keyword", type=str),
            OpenApiParameter(name="category_id", type=int),
            OpenApiParameter(name="answer_status", type=str),
            OpenApiParameter(name="sort", type=str, default="latest"),
        ],
        responses={200: AdminQuestionListResponseSerializer},
        tags=["Admin - Questions"],
    )
    def get(self, request: Request) -> Response:
        try:
            page = int(request.query_params.get("page", 1))
            size = int(request.query_params.get("size", 20))
        except ValueError:
            page, size = 1, 20

        search_keyword = request.query_params.get("search_keyword")
        cat_id_raw = request.query_params.get("category_id")
        category_id = int(cat_id_raw) if cat_id_raw else None
        answer_status = request.query_params.get("answer_status")
        sort = request.query_params.get("sort", "latest")

        result = AdminQuestionService.get_question_list(
            page=page,
            size=size,
            search_keyword=search_keyword,
            category_id=category_id,
            answer_status=answer_status,
            sort=sort,
        )

        serializer = AdminQuestionListResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
