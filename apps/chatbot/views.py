import json
import time

from typing import Any
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.http import StreamingHttpResponse
from django.db.models import QuerySet
from collections.abc import Iterator
from rest_framework.serializers import BaseSerializer

from .choices import MessageRoleChoices
from .models import ChatbotCompletions, ChatbotSessions
from .serializers import (
    ChatbotCompletionReadSerializer,
    ChatbotCompletionRequestSerializer,
    ChatbotSessionCreateSerializer,
    ChatbotSessionReadSerializer,
    SupportSessionCreateSerializer,
)


class ChatbotSessionListCreateView(generics.ListCreateAPIView[Any]):
    """
    <GET> /api/v1/chatbot/sessions : 로그인한 사용자의 챗봇 세션 목록 조회
    <POST> /api/v1/chatbot/sessions : 새 Q&A 챗봇 세션 생성
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[ChatbotSessions]:
        assert self.request.user.is_authenticated
        return ChatbotSessions.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self) -> type[BaseSerializer[Any]]:
        if self.request.method == "POST":
            return ChatbotSessionCreateSerializer
        return ChatbotSessionReadSerializer

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        assert self.request.user.is_authenticated
        serializer.save(user=self.request.user)


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
    <GET> /api/v1/chatbot/sessions/{session_id}/completions : 대화내역 조회
    <DELETE> /api/v1/chatbot/sessions/{session_id}/completions : 대화내역 삭제 (초기화)
    """

    permission_classes = [IsAuthenticated]

    # 대화내역 조회 <GET>
    def get(self, request: Request, session_id: int) -> Response:
        assert request.user.is_authenticated
        try:
            session = ChatbotSessions.objects.get(id=session_id, user=request.user)
        except ChatbotSessions.DoesNotExist:
            raise NotFound(detail=" 해당 세션을 찾을 수 없습니다.")
            # return Response({"error_detail": "챗봇 세션을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        completions = ChatbotCompletions.objects.filter(
            session_id=session_id,
            session__user=request.user
        ).order_by("created_at")
        
        serializer = ChatbotCompletionReadSerializer(completions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 대화 내역 초기화 <DELETE>
    def delete(self, request: Request, session_id:int) -> Response:
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = ChatbotSessions.objects.get(id=session_id, user=request.user)
        except ChatbotSessions.DoesNotExist:
            return Response({"error": "챗봇 세션을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user_message = str(serializer.validated_data["message"])

        # 사용자 질문 DB에 저장
        ChatbotCompletions.objects.create(
            session=session,
            role=MessageRoleChoices.USER,  # .choices ChatbotCompletions MessageRoleChoices
            message=user_message,
        )

        return StreamingHttpResponse(
            self._stream_gemini_response(session, user_message), content_type="text/event-stream"
        )

    def _stream_gemini_response(self, session: ChatbotSessions, user_message: str) ->Iterator[str]:
        full_response = ""

        dummy_text = f" 안녕하세요! AI 답변 스트리밍 테스트입니다. {user_message}"

        for char in dummy_text:
            full_response += char
            yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"

            time.sleep(0.06)

        ChatbotCompletions.objects.create(session=session, role=MessageRoleChoices.ASSISTANT, message=full_response)
        yield f"data: [DONE]\n\n"
