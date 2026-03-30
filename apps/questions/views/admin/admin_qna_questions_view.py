from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
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
        description="관리자용 질의응답 목록을 조회합니다. 카테고리, 답변 상태, 키워드 검색 및 정렬 기능을 제공합니다.",
        parameters=[
            OpenApiParameter(name="page", description="페이지 번호", type=int, default=1),
            OpenApiParameter(name="size", description="페이지당 항목 수", type=int, default=20),
            OpenApiParameter(name="search_keyword", description="제목 또는 내용 검색어", type=str),
            OpenApiParameter(name="category_id", description="카테고리 ID 필터", type=int),
            OpenApiParameter(name="answer_status", description="답변 상태 필터 (all, pending, completed)", type=str),
            OpenApiParameter(name="sort", description="정렬 기준 (latest, oldest, views)", type=str, default="latest"),
        ],
        responses={
            200: AdminQuestionListResponseSerializer,
            400: OpenApiResponse(
                description="잘못된 요청",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청 예시",
                        value={"error_detail": "유효하지 않은 목록 조회 요청입니다."},
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
                        value={"error_detail": "질의응답 목록 조회 권한이 없습니다."},
                    )
                ],
            ),
        },
        tags=["Admin_qna"],
    )
    def get(self, request: Request) -> Response:
        try:
            page = int(request.query_params.get("page", 1))
            size = int(request.query_params.get("size", 20))
        except ValueError:
            return Response(
                {"error_detail": "유효하지 않은 목록 조회 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        search_keyword = request.query_params.get("search_keyword")
        cat_id_raw = request.query_params.get("category_id")

        try:
            category_id = int(cat_id_raw) if cat_id_raw else None
        except ValueError:
            return Response(
                {"error_detail": "유효하지 않은 목록 조회 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
