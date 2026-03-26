import logging
from typing import Any

from django.conf import settings
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
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

from apps.chatbot.choices import ChatbotModelChoices
from apps.chatbot.exceptions import AIModelConnectionError, SessionNotFoundError
from apps.chatbot.models import ChatbotSessions
from apps.chatbot.serializers import (
    ChatbotCompletionRequestSerializer,
    ChatbotSessionDetailSerializer,
    ChatbotSessionListSerializer,
)
from apps.chatbot.services.chatbot_service import ChatbotService
from apps.questions.models import Questions

logger = logging.getLogger(__name__)


class ChatbotSessionListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["챗봇"],
        summary="QnA 챗봇 세션 목록 조회",
        description="현재 로그인한 유저의 모든 챗봇 세션을 최신순으로 반환합니다.",
        responses={200: ChatbotSessionListSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        sessions = ChatbotService.get_user_sessions(request.user)
        serializer = ChatbotSessionListSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["챗봇"],
        summary="QnA 챗봇 세션 생성",
        description="새로운 QnA 챗봇 세션을 생성하거나, 기존의 활성화된 세션을 반환합니다.",
        request=inline_serializer(
            name="ChatbotSessionCreateRequest",
            fields={"question_id": serializers.IntegerField(required=False, allow_null=True)},
        ),
        responses={
            201: OpenApiResponse(description="새로운 세션 생성 완료"),
            200: OpenApiResponse(description="기존 세션 반환 완료"),
        },
    )
    def post(self, request: Request) -> Response:
        """[QnA] 새로운 챗봇 세션 생성"""
        question_id = request.data.get("question_id")

        get_object_or_404(Questions, id=question_id)

        session, created = ChatbotSessions.objects.get_or_create(
            user=request.user,
            question_id=question_id,
            defaults={
                "title": "새 질문",
                "using_model": ChatbotModelChoices.GEMINI_2_0_FLASH_LITE_001.value,
            },
        )

        serializer = ChatbotSessionListSerializer(session)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK

        return Response(serializer.data, status=status_code)


# QnA 챗봇 세션 단일 조회 및 삭제
class ChatbotSessionDetailView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["챗봇"],
        summary="QnA 챗봇 세션 상세 조회",
        description="특정 세션의 상세 정보와 과거 대화 내역 모두 조회",
        responses={200: ChatbotSessionDetailSerializer, 404: OpenApiResponse(description="권한이 없거나 세션이 없음")},
    )
    def get(self, request: Request, session_id: int) -> Response:
        try:
            session = ChatbotService.get_session_detail_for_user(session_id, request.user)
            serializer = ChatbotSessionDetailSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SessionNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=["챗봇"],
        summary="QnA 챗봇 세션 삭제",
        description="특정 챗봇 세션과 속한 대화 내역을 삭제",
        responses={
            204: OpenApiResponse(description="삭제 성공 (본문 없음)"),
            404: OpenApiResponse(description="권한이 없거나 세션이 없음"),
        },
    )
    def delete(self, request: Request, session_id: int) -> Response:
        """"""
        try:
            ChatbotService.delete_session(session_id, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SessionNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class ChatbotCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    # <POST>
    @extend_schema(
        tags=["챗봇"],
        summary="QnA 챗봇 대화 생성 (스트리밍)",
        description="특정 세션에서 AI와 대화를 진행하고, SSE 스트리밍 방식으로 응답을 받습니다.",
        request=ChatbotCompletionRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.STR, description="text/event-stream 형식의 실시간 텍스트 조각 반환"
            ),
            400: OpenApiResponse(description="잘못된 요청 데이터"),
            404: OpenApiResponse(description="세션을 찾을 수 없음"),
        },
    )
    def post(self, request: Request, session_id: int) -> Response | StreamingHttpResponse:
        serializer = ChatbotCompletionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data["message"]

        api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not api_key:
            return Response({"error": "AI API 키가 설정되지 않았습니다."}, status=500)

        try:
            # ChatbotService의 Generator 받아옴
            stream_generator = ChatbotService.stream_db_response(
                session_id=session_id, user_message=user_message, api_key=str(getattr(settings, "GEMINI_API_KEY", ""))
            )

            return StreamingHttpResponse(stream_generator, content_type="text/event-stream")

        except SessionNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Chatbot QnA Stream Error: {e}")
            return Response({"error_detail": f"서버 에러: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotSupportCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["챗봇"],
        summary="CS 상담원 챗봇 (1회성 스트리밍)",
        description="DB 저장 없이 CS 전용 모델을 통해 1회성 답변을 스트리밍(SSE)로 반환합니다.",
        request=ChatbotCompletionRequestSerializer,
        responses={
            200: OpenApiResponse(response=OpenApiTypes.STR, description="text/event-stream 응답"),
        },
    )
    def post(self, request: Request) -> Response | StreamingHttpResponse:
        """[CS 상담] 세션 저장 없이 1회성 AI 응답 반환(스트리밍)"""
        serializer = ChatbotCompletionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data["message"]

        try:
            stream_generator = ChatbotService.stream_stateless_response(
                user_message=user_message, api_key=str(getattr(settings, "GEMINI_API_KEY", ""))
            )

            return StreamingHttpResponse(stream_generator, content_type="text/event-stream")
        except Exception as e:
            logger.error(f"Chatbot Support Stream Error: {e}")
            return Response({"error_detail": f"상담 봇 에러: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
