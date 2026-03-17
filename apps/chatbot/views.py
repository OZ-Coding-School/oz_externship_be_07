import json
import os
import time
from collections.abc import Iterator
from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from google import genai
from google.genai import types
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from apps.chatbot.exceptions import SessionNotFoundError
from apps.chatbot.services.chatbot_service import ChatbotService

from .choices import MessageRoleChoices
from .models import ChatbotCompletions, ChatbotSessions
from .serializers import (
    ChatbotCompletionReadSerializer,
    ChatbotCompletionRequestSerializer,
    ChatbotSessionCreateSerializer,
    ChatbotSessionReadSerializer,
    SupportSessionCreateSerializer,
)


class ChatbotCursorPagination(CursorPagination):
    ordering = "-created_at"


class ChatbotSessionListCreateView(generics.ListCreateAPIView[Any]):
    """
    <GET> /api/v1/chatbot/sessions : 로그인한 사용자의 챗봇 세션 목록 조회
    <POST> /api/v1/chatbot/sessions : 새 Q&A 챗봇 세션 생성
    """

    permission_classes = [IsAuthenticated]
    pagination_class = ChatbotCursorPagination

    def get_serializer_class(self) -> type[BaseSerializer[Any]]:
        if self.request.method == "POST":
            return ChatbotSessionCreateSerializer
        return ChatbotSessionReadSerializer

    def get_queryset(self) -> QuerySet[ChatbotSessions]:
        user_id = self.request.user.id
        assert user_id is not None
        return ChatbotSessions.objects.filter(user_id=user_id).order_by("-created_at")


class ChatbotSupportCreateView(generics.CreateAPIView[Any]):
    """
    <POST> /api/v1/chatbot/support : 시스템 (고객지원) 챗봇 세션 생성
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SupportSessionCreateSerializer

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        assert self.request.user.is_authenticated
        serializer.save(user=self.request.user)


class ChatbotSessionDetailView(generics.DestroyAPIView[Any]):
    """
    <DELETE> /api/v1/chatbot/sessions/{session_id} : 챗봇 세션 삭제
    """

    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "session_id"  # apps/chatbot/urls.py (line 13, line16) path parameter = session_id

    def get_queryset(self) -> QuerySet[ChatbotSessions]:
        assert self.request.user.is_authenticated
        return ChatbotSessions.objects.filter(user=self.request.user)


class ChatbotCompletionView(APIView):
    """
    <POST> /api/v1/chatbot/sessions/{session_id}/completions : AI 답변 생성, 스트리밍 방식
    """

    # <GET> /api/v1/chatbot/sessions/{session_id}/completions : 대화내역 조회
    # todo: <DELETE> /api/v1/chatbot/sessions/{session_id}/completions : 대화내역 삭제 (초기화)
    # 페이지네이션 할 때 수정

    permission_classes = [IsAuthenticated]

    # 대화내역 조회 <GET>
    def get(self, request: Request, session_id: int) -> Response:
        assert request.user.is_authenticated
        try:
            session = ChatbotService.get_user_sessions(session_id, request.user)
        except SessionNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        messages = ChatbotCompletions.objects.filter(session=session).order_by("created_at")

        paginator = ChatbotCursorPagination()
        paginated_messages = paginator.paginate_queryset(messages, request, view=self)

        serializer = ChatbotCompletionReadSerializer(paginated_messages, many=True)
        return paginator.get_paginated_response(serializer.data)

    # 대화 내역 초기화 <DELETE>
    def delete(self, request: Request, session_id: int) -> Response:
        assert request.user.is_authenticated
        try:
            session = ChatbotSessions.objects.get(id=session_id, user=request.user)
        except ChatbotSessions.DoesNotExist:
            raise NotFound(detail=" 해당 세션을 찾을 수 없습니다.")

        ChatbotCompletions.objects.filter(session_id=session_id, session__user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # AI 답변 생성 <POST>
    def post(self, request: Request, session_id: int) -> Response | StreamingHttpResponse:
        assert request.user.is_authenticated

        serializer = ChatbotCompletionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = ChatbotService.get_user_sessions(session_id=session_id, user=request.user)
        except SessionNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        api_key = getattr(settings, "GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return Response(
                {"error_detail": "서버에 AI API 키가 설정되지 않았습니다. 관리자에게 문의하세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user_message = str(serializer.validated_data["message"])

        # 사용자 질문 DB에 저장
        ChatbotService.save_user_message(session, user_message)

        return StreamingHttpResponse(
            self._stream_gemini_response(session, user_message, str(api_key)),
            content_type="text/event-stream",
            status=status.HTTP_201_CREATED,
        )

    def _stream_gemini_response(self, session: ChatbotSessions, user_message: str, api_key: str) -> Iterator[str]:

        client = genai.Client(api_key=api_key)
        full_response = ""

        try:
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=user_message,
            )

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield f"data: {json.dumps({'content': chunk.text}, ensure_ascii=False)}\n\n"

            ChatbotCompletions.objects.create(
                session=session,
                role=MessageRoleChoices.ASSISTANT,
                message=full_response,
            )

            yield "data: [DONE]\n\n"

        except Exception as e:
            error_message = f"AI 모델과 통신 중 오류가 발생했습니다. {str(e)}"
            yield f"data: {json.dumps({'error_detail': error_message}, ensure_ascii=False)}\n\n"
            yield f"data: [DONE]\n\n"
