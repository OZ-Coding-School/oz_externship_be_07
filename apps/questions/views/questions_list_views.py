from typing import Any, List

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.questions_serializers import (
    QuestionCreateResponseSerializer,
    QuestionCreateSerializer,
    QuestionListDetailSerializer,
    QuestionListSerializer,
    QuestionUpdateResponseSerializer,
    QuestionUpdateSerializer,
)
from apps.questions.services.questions_list_services import QuestionListService
from apps.questions.views.questions_create_views import QuestionCreateView
from apps.questions.views.questions_update_views import QuestionUpdateView


# 1. 목록 조회(GET) 및 등록(POST) 통합 관리
class QuestionListView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    serializer_class = QuestionListSerializer

    @extend_schema(
        tags=["qna"],
        summary="질문 조회",
        description="질문조회 작성 API",
        responses={200: QuestionListSerializer(many=True)},
        examples=[
            OpenApiExample(
                "성공예시(목록 조회)",
                value={
                    "results": [
                        {
                            "id": 1,
                            "category": {"id": 12, "depth": 2, "names": ["백엔드", "Django"]},
                            "author": {"id": 211, "nickname": "김오즈"},
                            "title": "Django ORM질문",
                            "content_preview": "ForeignKey 역참조 관련해서...",
                            "answer_count": 5,
                            "view_count": 27,
                            "created_at": "2025-03-10 10:22:33",
                        }
                    ]
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "실패 예시(검색 결과 없음)",
                value={"error_detail": "조회 가능한 질문이 존재하지 않습니다."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 필터 및 검색어 추출
        category_id_raw = request.query_params.get("category_id")
        category_id = None
        if category_id_raw:
            try:
                category_id = int(category_id_raw)
            except ValueError:
                return Response(
                    {"error_detail": "유효하지 않은 카테고리 ID입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        search_keyword = request.query_params.get("search")

        # 서비스 호출
        questions = QuestionListService.get_question_list(category_id=category_id, search_keyword=search_keyword)

        # 데이터 없을 경우 404 응답
        if not questions.exists():
            return Response({"error_detail": "조회 가능한 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 시리얼라이즈 및 반환
        serializer = QuestionListSerializer(questions, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["qna"],
        summary="질문 등록",
        description="질문등록 작성 API",
        request=QuestionCreateSerializer,
        responses={201: QuestionCreateResponseSerializer},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        view = QuestionCreateView()
        view.request = request
        return view.post(request, *args, **kwargs)


# 2. 상세 조회(GET) 및 수정(PUT) 통합 관리
class QuestionListDetailView(APIView):
    permission_classes = [AllowAny]

    serializer_class = QuestionListDetailSerializer

    @extend_schema(
        tags=["qna"],
        summary="질문 상세 조회",
        description="질문 상세조회을 조회하고 조회수를 1 올립니다.",
        responses={200: QuestionListDetailSerializer},
        examples=[
            OpenApiExample(
                "성공 예시 (상세조회)",
                value={
                    "id": 10501,
                    "title": "상세 제목입니다.",
                    "content": "상세 내용 본문입니다.",
                    "view_count": 28,
                    "created_at": "2025-03-10 10:22:33",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "실패 예시 (없는 ID)",
                value={"error_detail": "존재하지 않는 질문입니다."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def get(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        # 서비스 호출
        try:
            question = QuestionListService.get_question_detail(question_id)
            # 시리얼라이저 반환
            serializer = QuestionListDetailSerializer(question)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error_detail": "존재하지 않는 질문입니다."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=["qna"],
        summary="질문 수정",
        description="질문 수정 API",
        request=QuestionUpdateSerializer,
        responses={200: QuestionUpdateResponseSerializer},
    )
    def put(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        view = QuestionUpdateView()
        view.request = request
        return view.put(request, question_id)
