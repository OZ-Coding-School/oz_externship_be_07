import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.chatbot.choices import MessageRoleChoices
from apps.chatbot.exceptions import SessionNotFoundError
from apps.chatbot.models import ChatbotCompletions, ChatbotSessions

User = get_user_model()
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
        사용자의 메시지를 DB에 저장
        """
        return ChatbotCompletions.objects.create(
            session=session,
            role=MessageRoleChoices.USER,
            message=message,
        )
