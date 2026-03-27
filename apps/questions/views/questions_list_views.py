from typing import Any

from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
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

    def get_permissions(self) -> list[BasePermission]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    serializer_class = QuestionListSerializer

    @extend_schema(
        tags=["Qna"],
        summary="질문 조회",
        description="질문 목록을 조회하며, 전역 설정된 페이지네이션이 적용됩니다.",
        parameters=[
            OpenApiParameter(name="category_id", description="카테고리 ID필터", type=int),
            OpenApiParameter(name="search", description="검색어", type=str),
            OpenApiParameter(name="answer_status", description="답변 상태(answered/unanswered)", type=str),
            OpenApiParameter(name="sort", description="정렬(latest: 최신순, views: 조회수순)", type=str),
            OpenApiParameter(name="size", description="한 페이지 당 보여줄 개수", type=int),
            OpenApiParameter(name="page", description="페이지 번호", type=int),
        ],
        responses={200: QuestionListSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        # 필터 및 검색어 추출
        category_id_raw = request.query_params.get("category_id")
        category_id = None
        if category_id_raw:
            try:
                category_id = int(category_id_raw)
            except (ValueError, TypeError):
                return Response(
                    {"error_detail": "유효하지 않은 카테고리 ID입니다. 숫자를 입력해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        search_keyword = request.query_params.get("search")
        answer_status = request.query_params.get("answer_status")
        sort_by = request.query_params.get("sort", "latest")
        # 서비스 호출
        questions = QuestionListService.get_question_list(
            category_id=category_id, search_keyword=search_keyword, answer_status=answer_status, sort_by=sort_by
        )

        # 페이지네이션 적용
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(questions, request)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # 시리얼라이즈 및 반환
        serializer = QuestionListSerializer(questions, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Qna"],
        summary="질문 등록",
        description="새로운 질문을 등록합니다.",
        request=QuestionCreateSerializer,
        responses={201: QuestionCreateResponseSerializer},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return QuestionCreateView.create_question(request)


# 2. 상세 조회(GET) 및 수정(PUT) 통합 관리
class QuestionListDetailView(APIView):
    def get_permissions(self) -> list[BasePermission]:
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    serializer_class = QuestionListDetailSerializer

    @extend_schema(
        tags=["Qna"],
        summary="질문 상세 조회",
        description="질문 상세조회을 조회하고 조회수를 1 올립니다.",
        responses={200: QuestionListDetailSerializer},
    )
    def get(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        # 서비스 호출
        try:
            question = QuestionListService.get_question_detail(question_id)
            # 시리얼라이저 반환
            serializer = self.serializer_class(question)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error_detail": "존재하지 않는 질문입니다."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=["Qna"],
        summary="질문 수정",
        description="기존 질문 내용을 수정합니다.",
        request=QuestionUpdateSerializer,
        responses={200: QuestionUpdateResponseSerializer},
    )
    def put(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        return QuestionUpdateView.update_question(request, question_id)
