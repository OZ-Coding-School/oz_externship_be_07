from typing import Any, cast

from django.contrib.auth import get_user_model

from apps.chatbot.choices import MessageRoleChoices
from apps.chatbot.exceptions import SessionNotFoundError
from apps.chatbot.models import ChatbotCompletions, ChatbotSessions

User = get_user_model()


class ChatbotService:

    @staticmethod
    def get_user_sessions(session_id: int, user: Any) -> ChatbotSessions:
        """
        session id 와 유저 정보를 받아서 활성화된 챗봇 세션 조회
        todo: Redis 캐싱 조회 로직 추가
        """
        try:
            return ChatbotSessions.objects.get(id=session_id, user=user)
        except ChatbotSessions.DoesNotExist as exc:
            raise SessionNotFoundError("해당 챗봇 세션을 찾을 수 없습니다.") from exc

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
