from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Iterator, cast

from django.conf import settings
from django.core.cache import caches
from django.db.models import QuerySet
from google import genai

from apps.chatbot.choices import BotTypeChoices, ChatbotModelChoices, MessageRoleChoices
from apps.chatbot.exceptions import ChatbotThrottledError, SessionNotFoundError
from apps.chatbot.models import ChatbotCompletions, ChatbotSessions
from apps.chatbot.prompts.support_context import SUPPORT_SYSTEM_PROMPT

chatbot_cache = caches["chatbot"]
logger = logging.getLogger(__name__)


class ChatbotService:

    @classmethod
    def stream_stateless_response(cls, user_message: str, api_key: str) -> Iterator[str]:
        """[CS 상담 전용]DB저장 없는 1회성 스트리밍"""

        client = genai.Client(api_key=api_key)

        target_model = ChatbotModelChoices.GEMINI_2_5_FLASH_LITE.value

        system_instruction = SUPPORT_SYSTEM_PROMPT if SUPPORT_SYSTEM_PROMPT else "오즈코딩스쿨의 친절한 상담원입니다."

        formatted_contents = [{"role": "user", "parts": [{"text": user_message}]}]

        # AI 스트리밍 요청
        response = client.models.generate_content_stream(
            model=target_model,
            contents=cast(list[Any], formatted_contents),
            config={"system_instruction": system_instruction, "temperature": 0.7},
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    @classmethod
    def get_session_or_404(cls, session_id: int) -> ChatbotSessions:
        """DB에서 세션을 가져오고 없으면 404 에러 발생"""
        try:
            return ChatbotSessions.objects.get(id=session_id)
        except ChatbotSessions.DoesNotExist:
            raise SessionNotFoundError(f"ID가 {session_id}인 세션을 찾을 수 없습니다.")

    @classmethod
    def stream_db_response(cls, session_id: int, user_message: str, api_key: str) -> Iterator[str]:
        """[QnA 전용] DB 기반 스트리밍 + Redis Lock 구조"""

        # 클라 초기화
        client = genai.Client(api_key=api_key)

        # Redis Lock 체크로 동시 요청 방지
        lock_key = f"chatbot:responding:{session_id}"
        if chatbot_cache.get(lock_key):
            raise ChatbotThrottledError("AI가 아직 이전 질문에 답변중입니다. 잠시 후 다시 시도해주세요.")

        chatbot_cache.set(lock_key, True, timeout=180)

        try:
            # 세션 조회, 유저 질문 db에 먼저 저장
            session = cls.get_session_or_404(session_id)
            ChatbotCompletions.objects.create(
                session=session,
                message=user_message,
                role=MessageRoleChoices.USER.value,
            )
            # 프폼프트에 들어갈 질문글 컨텍스트 가져오기
            question_title = session.question.title if session.question else "일반 프로그래밍 질문"
            question_content = session.question.content if session.question else ""

            # 모델 및 프롬프트 세팅
            target_model = session.using_model
            system_instruction = f"""
            당신은 오즈코딩스쿨의 전문적인 프로그래밍 QnA 튜터입니다.
            아래는 사용자가 현재 열람 중인 질문글 정보입니다.
            [제목]: {question_title}
            [내용]: {question_content}
            """

            # 이전 대화 내역 DB에서 불러오기
            history_qs = session.completions.all().order_by("created_at")
            formatted_contents = [
                {
                    "role": "user" if message_row.role == MessageRoleChoices.USER.value else "model",
                    "parts": [{"text": message_row.message}],
                }
                for message_row in history_qs
            ]

            # AI 스트리밍 요청
            response = client.models.generate_content_stream(
                model=target_model,
                contents=cast(list[Any], formatted_contents),
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                },
            )

            # chunk 합체
            final_ai_message = ""
            for chunk in response:
                if chunk.text:
                    final_ai_message += chunk.text
                    yield chunk.text

            # 스트리밍 끝, AI답변을 db에 저장
            ChatbotCompletions.objects.create(
                session=session, message=final_ai_message, role=MessageRoleChoices.ASSISTANT.value
            )

        except Exception as e:
            logger.error(f"Chatbot Service Error: {e}")
            raise e

        finally:
            # 어쨋든 lock 키 삭제
            chatbot_cache.delete(lock_key)

    @classmethod
    def get_user_sessions(cls, user: Any) -> QuerySet[ChatbotSessions]:
        """[조회] 특정 유저의 챗봇 세션 목록 조회 최신순"""
        return ChatbotSessions.objects.filter(user=user).order_by("-updated_at")

    @classmethod
    def get_session_detail_for_user(cls, session_id: int, user: Any) -> ChatbotSessions:
        """[조회] 특정 유저의 단일 세션과 대화내역 조회"""
        try:
            qs: QuerySet[ChatbotSessions] = ChatbotSessions.objects.prefetch_related("completions")
            return qs.get(id=session_id, user=user)
        except ChatbotSessions.DoesNotExist:
            raise SessionNotFoundError("접근 권한이 없거나, 존재하지 않는 세션입니다.")

    @classmethod
    def delete_session(cls, session_id: int, user: Any) -> None:
        """[삭제] 세션 삭제, 대화 내역 자동 삭제(Cascade)"""
        session = cls.get_session_detail_for_user(session_id, user)
        session.delete()


# class ChatbotCacheManager:
#     """Redis 키 생성 및 관리 전담 클래스"""

#     @staticmethod
#     def get_history_key(bot_type: str, session_id: int) -> str:
#         return f"chatbot:{bot_type.lower()}:history:{session_id}"

#     @staticmethod
#     def get_limit_key(bot_type: str, session_id: int) -> str:
#         return f"chatbot:{bot_type.lower()}:limit:{session_id}"

#     @staticmethod
#     def get_usage_count_key(bot_type: str, session_id: int) -> str:
#         """횟수 제한용 Redis 키 생성"""
#         return f"chatbot:{bot_type.lower()}:count:{session_id}"
