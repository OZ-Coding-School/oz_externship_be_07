import os
import uuid
from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.chatbot.choices import BotTypeChoices
from apps.chatbot.services.chatbot_service import ChatbotService

from .serializers import ChatbotCompletionRequestSerializer


class ChatbotSessionCreateView(APIView):

    """
    [무상태 챗봇 세션 발급 뷰] 1회용 고유 식별자(UUID)만 발급
    """

    permission_classes = [IsAuthenticated]
    @extend_schema(summary="새 챗봇 세션 생성", responses={201: Any})
    def post(self, request: Request) -> Response:
        new_session_id = str(uuid.uuid4())
        return Response({"session_id": new_session_id}, status=status.HTTP_201_CREATED)

@extend_schema_view(
    POST=extend_schema(summary="AI 답변 생성, 스트리밍"),
    GET=extend_schema(summary="대화내역 조회"),
    DELETE=extend_schema(summary="대화내역 삭제 (초기화)")
)
class ChatbotCompletionView(APIView):
    permission_classes = [IsAuthenticated]
    """
    <POST> /api/v1/chatbot/sessions/{session_id}/completions : AI 답변 생성(최대 2회), 스트리밍 방식
    <GET> /api/v1/chatbot/sessions/{session_id}/completions : 현재 세션 대화내역 (Redis)
    <DELETE> /api/v1/chatbot/sessions/{session_id}/completions : 세션 종료 (Redis 삭제)
    """
    # 대화내역 조회 <GET>
    @extend_schema(
        tags=["Chatbot (챗봇)"],
        summary="대화내역 조회 <GET>",
        request=ChatbotCompletionRequestSerializer,
        parameters=[
            OpenApiParameter(
                name="bot_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                enum=BotTypeChoices.values, 
            ),
        ]
    )
    def get(self, request: Request, bot_type: str, session_id: str) -> Response:
        if bot_type not in BotTypeChoices.values:
            return Response({"error_detail": "잘못된 챗봇 타입입니다."}, status=status.HTTP_400_BAD_REQUEST)

        messages = ChatbotService.get_ephemeral_history(bot_type, str(session_id))

        if not messages:
            return Response(
                {"error_detail": "세션이 만료되었거나 대화 내역이 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"results": messages}, status=status.HTTP_200_OK)

    # <DELETE>
    @extend_schema(
        tags=["Chatbot (챗봇)"],
        summary="챗봇 세션 종료",
        request=ChatbotCompletionRequestSerializer,
        parameters=[
            OpenApiParameter(
                name="bot_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                enum=BotTypeChoices.values, 
            ),
        ]
    )
    def delete(self, request: Request, bot_type: str, session_id: str) -> Response:
        assert request.user.is_authenticated

        if bot_type not in BotTypeChoices.values:
            return Response({"error_detail": "잘못된 챗봇 타입입니다."}, status=status.HTTP_400_BAD_REQUEST)

        ChatbotService.delete_ephemeral_session(bot_type, str(session_id))

        return Response(status=status.HTTP_204_NO_CONTENT)

    # AI 답변 생성 <POST>
    @extend_schema(
        tags=["Chatbot (챗봇)"],
        summary="AI 답변 생성 (Streaming)",
        request=ChatbotCompletionRequestSerializer,
        # 🔥 이 부분을 추가하세요!
        parameters=[
            OpenApiParameter(
                name="bot_type",
                type=str,
                location=OpenApiParameter.PATH,
                description="어떤 챗봇과 대화할지 선택하세요. (예: qna, support)",
                enum=BotTypeChoices.values,
            ),
            OpenApiParameter(
                name="session_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="발급받은 세션 ID (UUID)",
            )
        ]
    )
    def post(self, request: Request, bot_type: str, session_id: str) -> Response | StreamingHttpResponse:
        serializer = ChatbotCompletionRequestSerializer(data=request.data)

        assert request.user.is_authenticate

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_message = serializer.validated_data.get("message")

        bot_type = serializer.validated_data.get("bot_type", "qna")

        if bot_type not in BotTypeChoices.values:
            return Response({"error_detail": "잘못된 챗봇 URL 경로입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if bot_type == "qna":
            try:
                ChatbotService.check_and_increment_limit(session_id, user=request.user)
            except PermissionError as e:
                return Response({"error_detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not api_key:
            return Response(
                {"error_detail": "API 키 오류."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Gemini API와 통신하여 AI 답변을 스트리밍으로 받아옴
        stream = ChatbotService.stream_ephemeral_response(
            session_id=session_id,
            user_message=user_message,
            api_key=str(api_key),
            bot_type=bot_type,
        )

        return StreamingHttpResponse(
            stream,
            content_type="text/event-stream",
            status=status.HTTP_201_CREATED,
        )
