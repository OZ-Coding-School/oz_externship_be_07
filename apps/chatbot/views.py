import json
import logging
import uuid
from typing import Any

from django.conf import settings
from django.http import StreamingHttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
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

logger = logging.getLogger(__name__)


"""
[0식] QnA 챗봇 세션 목록 조회 및 생성
"""
class ChatbotSessionListCreationView(APIView):
    def get(self,request: Request)  -> Response :
        pass                            # TODO: DB에서 세션목록 가져오기
    
    def post(self,request: Request):
        pass                            # TODO: DB에 새 세션 만들기


"""
[0식] QnA 챗봇 세션 단일 조회 및 삭제
"""
class ChatbotSessionDetailView(APIView):
    def get(self, request: Request, session_id: str):
        pass                            # TODO: DB에서 특정 세션 가져오기


class ChatbotCompletionView(APIView):
    permission_classes = [IsAuthenticated]
    """
    <GET> /api/v1/chatbot/sessions/{session_id}/completions
    <DELETE> /api/v1/chatbot/sessions/{session_id}/completions
    <POST> /api/v1/chatbot/sessions/{session_id}/completions
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
    def get(self, request: Request, session_id: str) -> Response:
        pass                            # TODO: DB에서 ChatbotCompletions 내역 가져오기

    # <POST>
    @extend_schema(
        tags=["Chatbot (챗봇)"],
        summary="AI 답변 생성 (Streaming)",
        request=ChatbotCompletionRequestSerializer,
        description="챗봇에게 메시지를 보내고 답변을 받음(스트리밍).",
        responses={201: OpenApiResponse(description="스트리밍 응답 (text/event-stream)")},
    )
    def post(self, request: Request, session_id: str) -> Response | StreamingHttpResponse:
        pass                        # TODO: AI 스트리밍 및 DB에 ChatbotCompletions 저장
    
        # api_key = getattr(settings, "GEMINI_API_KEY", None)
        # if not api_key:
        #     return Response(
        #         {"error_detail": "API 키 오류."},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     )

        # # Gemini API와 통신하여 응답 반환 (스트리밍)
        # try:
        #     stream = ChatbotService.stream_ephemeral_response(
        #         session_id=session_id,
        #         user_message=user_message,
        #         api_key=str(api_key),
        #         bot_type=bot_type_lower,
        #     )

        #     return StreamingHttpResponse(
        #         stream,
        #         content_type="text/event-stream",
        #         status=status.HTTP_201_CREATED,
        #     )
        # except Exception as e:
        #     logger.error(f"Chatbot View Error: {e}")
        #     return Response(
        #         {"error_detail": "챗봇 응답 생성 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )



#
# Deprecated.
#
# class ChatbotSessionCreateView(APIView):
#     """
#     [무상태 챗봇 세션 발급] 1회용 고유 식별자(UUID)만 발급
#     """

#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         tags=["Chatbot (챗봇)"],
#         summary="챗봇 세션 생성",
#         description="새로운 챗봇 대화를 위한 1회용 UUID 세션을 발급합니다.",
#         request=None,
#         responses={
#             201: inline_serializer(name="SessionCreateResponse", fields={"session_id": serializers.UUIDField()})
#         },
#     )
#     def post(self, request: Request) -> Response:
#         new_session_id = str(uuid.uuid4())
#         return Response({"session_id": new_session_id}, status=status.HTTP_201_CREATED)