import json
import logging
from typing import Any, Iterator

from django.core.cache import cache
from django.db.models import QuerySet
from google import genai

from apps.chatbot.choices import MessageRoleChoices
from apps.chatbot.exceptions import SessionNotFoundError
from apps.chatbot.models import ChatbotCompletions, ChatbotSessions

logger = logging.getLogger(__name__)


class ChatbotService:

    @staticmethod
    def get_user_sessions(session_id: int, user: Any) -> ChatbotSessions:
        """
        session id 와 유저 정보를 받아서 활성화된 챗봇 세션 조회
        Redis 캐시에서 먼저 조회하고, 없으면 Postgres 에서 조회하여 Redis에 캐싱
        """
        cache_key = f"chatbot_session_{session_id}_user_{user.id}"

        # Redis 캐시 조회
        try:
            cached_session = cache.get(cache_key)

            if isinstance(cached_session, ChatbotSessions):
                return cached_session
        except Exception as e:
            logger.error(f"Redis 캐시 조회 실패, Postgres에서 조회 시도: {e}")

        # 캐시에 없거나 Redis 오류 시 Postgres에서 조회
        try:
            session = ChatbotSessions.objects.get(id=session_id, user=user)
        except ChatbotSessions.DoesNotExist as exc:
            raise SessionNotFoundError("해당 세션을 찾을 수 없습니다.") from exc

        # 조회된 세션을 Redis 캐시에 저장
        try:
            cache.set(cache_key, session, timeout=3600)  # 1시간 캐시
        except Exception as e:
            logger.error(f"Redis 캐시 저장 실패: {e}")

        return session

    @staticmethod
    def save_user_message(session: ChatbotSessions, message: str) -> ChatbotCompletions:
        """
        사용자의 질문을 DB에 저장
        """
        return ChatbotCompletions.objects.create(
            session=session,
            role=MessageRoleChoices.USER,
            message=message,
        )

    @staticmethod
    def get_session_messages(session: ChatbotSessions) -> list[ChatbotCompletions]:
        """
        특정 세션의 전체 대화 내역 조회
        """
        return list(ChatbotCompletions.objects.filter(session=session).order_by("created_at"))

    @staticmethod
    def clear_session_messages(session_id: int, user: Any) -> None:
        """
        특정 세션의 대화 내역(Completions) 전체 초기화
        """
        session = ChatbotService.get_user_sessions(session_id, user)
        ChatbotCompletions.objects.filter(session=session).delete()

    @staticmethod
    def stream_gemini_response(session: ChatbotSessions, user_message: str, api_key: str) -> Iterator[str]:
        """
        Gemini API와 통신하여 AI 답변을 스트리밍으로 받아오고, 최종 답변을 DB에 저장
        """

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
        except Exception as e:
            error_msg = f"AI 답변 생성 중 오류가 발생했습니다: {str(e)}"
            yield f"data: {json.dumps({'error_detail': error_msg}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        try:
            ChatbotCompletions.objects.create(
                session=session,
                role=MessageRoleChoices.ASSISTANT,
                message=full_response,
            )
        except Exception as db_error:
            logger.error(f"DB 저장 실패: {db_error}")

        yield "data: [DONE]\n\n"
