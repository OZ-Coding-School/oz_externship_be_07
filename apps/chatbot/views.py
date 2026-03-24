import os
import uuid
from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.choices import BotTypeChoices
from apps.chatbot.services.chatbot_service import ChatbotService

from .serializers import ChatbotCompletionRequestSerializer


class ChatbotSessionCreateView(APIView):
    """
    [무상태 챗봇 세션 발급] 1회용 고유 식별자(UUID)만 발급
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot (챗봇)"],
        summary="챗봇 세션 생성",
        description="새로운 챗봇 대화를 위한 1회용 UUID 세션을 발급합니다.",
        request=None,
        responses={
            201: inline_serializer(name="SessionCreateResponse", fields={"session_id": serializers.UUIDField()})
        },
    )
    def post(self, request: Request) -> Response:
        new_session_id = str(uuid.uuid4())
        return Response({"session_id": new_session_id}, status=status.HTTP_201_CREATED)


class ChatbotCompletionView(APIView):
    permission_classes = [IsAuthenticated]
    """
    <GET> /api/v1/chatbot/sessions/{session_id}/completions : 현재 세션 대화내역 조회
    <DELETE> /api/v1/chatbot/sessions/{session_id}/completions : 세션 종료 (Redis 삭제)
    <POST> /api/v1/chatbot/sessions/{session_id}/completions : AI 답변 생성(최대 2회), 스트리밍 방식
    """

    # 대화내역 조회 <GET>
    @extend_schema(
        tags=["Chatbot (챗봇)"],
        description="특정 세션의 챗봇 대화 내역을 조회합니다.",
        summary="대화내역 조회 <GET>",
        responses={
            200: OpenApiResponse(description="대화 내역 리스트 반환"),
            404: OpenApiResponse(description="세션 만료"),
        },
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
        description="특정 세션의 대화 내역을 삭제합니다.",
        responses={204: OpenApiResponse(description="성공적으로 삭제됨")},
    )
    def delete(self, request: Request, bot_type: str, session_id: str) -> Response:
        assert request.user.is_authenticated

        if bot_type not in BotTypeChoices.values:
            return Response({"error_detail": "잘못된 챗봇 타입입니다."}, status=status.HTTP_400_BAD_REQUEST)

        ChatbotService.delete_ephemeral_session(bot_type, str(session_id))

        return Response(status=status.HTTP_204_NO_CONTENT)

    # <POST>
    @extend_schema(
        tags=["Chatbot (챗봇)"],
        summary="AI 답변 생성 (Streaming)",
        request=ChatbotCompletionRequestSerializer,
        description="챗봇에게 메시지를 보내고 답변을 받음(스트리밍).",
        parameters=[
            OpenApiParameter(
                name="bot_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,  # URL 경로 변수임을 명시
                description="어떤 챗봇과 대화할지 선택하세요. (예: qna, support)",
                enum=BotTypeChoices.values,
            ),
            OpenApiParameter(
                name="session_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="발급받은 세션 ID (UUID)",
            ),
        ],
        responses={201: OpenApiResponse(description="스트리밍 응답 (text/event-stream)")},
    )
    def post(self, request: Request, bot_type: str, session_id: str) -> Response | StreamingHttpResponse:
        serializer = ChatbotCompletionRequestSerializer(data=request.data)

        if serializer.is_valid():
            user_message = serializer.validated_data.get("message")

            if bot_type == "qna":
                try:
                    ChatbotService.check_and_increment_limit(bot_type, session_id, user=request.user)
                except PermissionError as e:
                    return Response({"error_detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

            if bot_type not in BotTypeChoices.values:
                return Response({"error_detail": "잘못된 경로입니다."}, status=status.HTTP_400_BAD_REQUEST)

        api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not api_key:
            return Response(
                {"error_detail": "API 키 오류."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Gemini API와 통신하여 응답 반환 (스트리밍)
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
