import logging
from typing import cast

from django.http import StreamingHttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.models import User

from apps.chatbot.exceptions import (
    ChatbotThrottledError,
    CompletionLimitExceededError,
    SessionNotFoundError,
)
from apps.chatbot.pagination import ChatbotCursorPagination
from apps.chatbot.serializers import (
    ChatbotCompletionRequestSerializer,
    ChatbotCompletionSerializer,
    ChatbotSessionSerializer,
)
from apps.chatbot.services.chatbot_service import ChatbotService
from apps.questions.models import Questions

logger = logging.getLogger(__name__)


class ChatbotSessionListCreateView(APIView):
    """QnA 챗봇 세션 목록 조회 / 생성"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="QnA 챗봇 세션 목록 조회",
        parameters=[
            OpenApiParameter(name="cursor", type=str, description="커서"),
            OpenApiParameter(name="page_size", type=int, description="페이지 크기", default=10),
        ],
        responses={200: ChatbotSessionSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        sessions = ChatbotService.get_user_sessions(cast(User, request.user))
        paginator = ChatbotCursorPagination()
        page = paginator.paginate_queryset(sessions, request)
        serializer = ChatbotSessionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=["chatbot"],
        summary="QnA 챗봇 세션 생성",
        request=ChatbotCompletionRequestSerializer,
        responses={
            201: ChatbotSessionSerializer,
            200: ChatbotSessionSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        question_id = int(request.data.get("question_id", 0))

        try:
            session, created = ChatbotService.create_session(cast(User, request.user), question_id)
        except Questions.DoesNotExist:
            return Response(
                {"error_detail": "등록된 질문이(가) 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ChatbotSessionSerializer(session)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)


class ChatbotSessionDetailView(APIView):
    """QnA 챗봇 세션 삭제"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="QnA 챗봇 세션 삭제",
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            404: OpenApiResponse(description="세션이 없음"),
        },
    )
    def delete(self, request: Request, session_id: int) -> Response:
        try:
            ChatbotService.delete_session(session_id, cast(User, request.user))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SessionNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class ChatbotCompletionListCreateView(APIView):
    """QnA 챗봇 대화내역 조회 / 대화 생성 (SSE 스트리밍)"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="QnA 챗봇 대화내역 조회",
        parameters=[
            OpenApiParameter(name="cursor", type=str, description="커서"),
            OpenApiParameter(name="page_size", type=int, description="페이지 크기", default=10),
        ],
        responses={200: ChatbotCompletionSerializer(many=True)},
    )
    def get(self, request: Request, session_id: int) -> Response:
        try:
            completions = ChatbotService.get_session_completions(session_id, cast(User, request.user))
        except SessionNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        paginator = ChatbotCursorPagination()
        page = paginator.paginate_queryset(completions, request)
        serializer = ChatbotCompletionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=["chatbot"],
        summary="QnA 챗봇 대화 생성 (SSE 스트리밍)",
        request=ChatbotCompletionRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=OpenApiTypes.STR,
                description='SSE 스트리밍: data: {"content": "텍스트"}\\n\\n → data: [DONE]\\n\\n',
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="세션을 찾을 수 없음"),
            429: OpenApiResponse(description="이전 질문 답변 중"),
        },
    )
    def post(self, request: Request, session_id: int) -> Response | StreamingHttpResponse:
        serializer = ChatbotCompletionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data["message"]

        try:
            # generator 생성 전에 사전 검증 (여기서 에러 나면 except에서 잡힘)
            ChatbotService.validate_qna_request(session_id, user_message)
            stream = ChatbotService.stream_qna_response(session_id, user_message)
            return StreamingHttpResponse(stream, content_type="text/event-stream", status=201)

        except SessionNotFoundError:
            return Response(
                {"error_detail": "챗봇 세션이 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except CompletionLimitExceededError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except ChatbotThrottledError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception as e:
            logger.error(f"Chatbot QnA Stream Error: {e}")
            return Response(
                {"error_detail": "서버 에러가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChatbotSupportView(APIView):
    """CS 상담 챗봇 (1회성 SSE 스트리밍, 세션 저장 없음)"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="CS 상담 챗봇 (1회성 스트리밍)",
        request=ChatbotCompletionRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.STR,
                description='SSE 스트리밍: data: {"content": "텍스트"}\\n\\n → data: [DONE]\\n\\n',
            ),
        },
    )
    def post(self, request: Request) -> Response | StreamingHttpResponse:
        serializer = ChatbotCompletionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data["message"]

        try:
            ChatbotService.validate_support_request(user_message)
            stream = ChatbotService.stream_support_response(user_message)
            return StreamingHttpResponse(stream, content_type="text/event-stream")
        except Exception as e:
            logger.error(f"Chatbot Support Error: {e}")
            return Response(
                {"error_detail": "상담 봇 에러가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
