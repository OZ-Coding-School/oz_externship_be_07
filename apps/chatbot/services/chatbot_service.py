import json
import logging
from typing import Any, Iterator, cast

from django.conf import settings
from django.core.cache import caches
from google import genai

from apps.chatbot.choices import BotTypeChoices, ChatbotModelChoices, MessageRoleChoices
from apps.chatbot.prompts.support_context import SUPPORT_SYSTEM_PROMPT

chatbot_cache = caches["chatbot"]
logger = logging.getLogger(__name__)


class ChatbotCacheManager:
    """Redis 키 생성 및 관리 전담 클래스"""

    @staticmethod
    def get_history_key(bot_type: str, session_id: str) -> str:
        return f"chatbot:{bot_type.lower()}:history:{session_id}"

    @staticmethod
    def get_limit_key(bot_type: str, session_id: str) -> str:
        return f"chatbot:{bot_type.lower()}:limit:{session_id}"

    @staticmethod
    def get_usage_count_key(bot_type: str, session_id: str) -> str:
        """횟수 제한용 Redis 키 생성"""
        return f"chatbot:{bot_type.lower()}:count:{session_id}"


class ChatbotService:
    SESSION_TTL = 3600

    @staticmethod
    def check_and_increment_limit(bot_type: str, session_id: str, user: Any) -> None:
        """
        QnA 챗봇에 질문한 횟수를 확인하고 1 증가 (최대 3회)
        """

        count_key = ChatbotCacheManager.get_usage_count_key(bot_type, session_id)
        current_count = caches["chatbot"].get(count_key, 0)

        if current_count >= 3:
            raise PermissionError(
                "질문 가능 횟수(3회)를 초과했습니다. 궁금하신 사항은 질문 게시판을 이용하시기 바랍니다."
            )

        caches["chatbot"].set(count_key, current_count + 1, timeout=3600)

    @classmethod
    def get_ephemeral_history(cls, bot_type: str, session_id: str) -> list[dict[str, Any]]:
        """
        Redis에서 특정 세션의 대화 내역 조회
        """
        history_key = ChatbotCacheManager.get_history_key(bot_type, session_id)
        return chatbot_cache.get(history_key) or []

    @classmethod
    def delete_ephemeral_session(cls, bot_type: str, session_id: str) -> None:
        """
        특정 봇 타입의 특정 세션 Redis 캐시 초기화
        """
        history_key = ChatbotCacheManager.get_history_key(bot_type, session_id)
        caches["chatbot"].delete(history_key)

    @classmethod
    def delete_ephemeral_history(cls, bot_type: str, session_id: str) -> None:
        history_key = ChatbotCacheManager.get_history_key(bot_type, session_id)
        caches["chatbot"].delete(history_key)

    @staticmethod
    def _append_to_history(bot_type: str, session_id: str, role: str, message: str) -> None:
        """
        Redis 대화내역에 새로운 메시지 추가 (내부용)
        """
        history_key = ChatbotCacheManager.get_history_key(bot_type, session_id)
        history = chatbot_cache.get(history_key, [])
        history.append({"role": role, "message": message})
        chatbot_cache.set(history_key, history, timeout=ChatbotService.SESSION_TTL)

    @classmethod
    def stream_ephemeral_response(
        cls,
        session_id: str,
        user_message: str,
        api_key: str,
        bot_type: str = "qna",
    ) -> Iterator[str]:
        """
        [통합 챗봇 스트리밍] bot_type에 따라 프롬프트를 다르게 주입, 스트리밍 반환.
            - bot_type="qna": 기존 대화 내역 사용,
            - bot_type="support": CS 전용 시스템 프롬프트 주입
        """
        ChatbotService._append_to_history(bot_type, session_id, MessageRoleChoices.USER.value, user_message)

        target_model = ChatbotModelChoices.GEMINI_2_0_FLASH_LITE_001.value
        system_instruction = "당신은 오즈코딩스쿨의 전문적인 프로그래밍 QnA 튜터입니다."

        if bot_type == BotTypeChoices.SUPPORT.value:
            system_instruction = (
                SUPPORT_SYSTEM_PROMPT if SUPPORT_SYSTEM_PROMPT else "오즈코딩스쿨의 친절한 상담원입니다."
            )
            target_model = ChatbotModelChoices.GEMINI_2_5_FLASH.value

        raw_history = ChatbotService.get_ephemeral_history(bot_type, session_id)
        formatted_contents = [
            {
                "role": "user" if msg["role"] == MessageRoleChoices.USER.value else "model",
                "parts": [{"text": msg["message"]}],
            }
            for msg in raw_history
        ]

        client = genai.Client(api_key=api_key)
        full_response = ""

        history_key = ChatbotCacheManager.get_history_key(bot_type, session_id)
        history = caches["chatbot"].get(history_key, [])

        history.append({"role": "user", "message": user_message})  # 유저 메시지 저장
        full_ai_response = ""

        try:
            logger.info(f"Chatbot Start | Type: {bot_type} | Model: {target_model}")

            response = client.models.generate_content_stream(
                model=target_model,
                contents=cast(list[Any], formatted_contents),
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.7,
                    "max_output_tokens": 1000,  # 무한 루프 방지용 토큰 제한
                },
            )

            for chunk in response:
                # 차단되었거나 텍스트가 없는 경우 처리
                text = getattr(chunk, "text", None)
                if text:
                    full_response += text
                    payload = {"role": MessageRoleChoices.ASSISTANT.value, "content": text}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            # AI 응답 저장
            if full_response.strip():
                ChatbotService._append_to_history(
                    bot_type, session_id, MessageRoleChoices.ASSISTANT.value, full_response
                )
            else:
                raise ValueError("AI가 빈 응답을 생성했습니다.")

        except Exception as e:
            logger.error(f"[챗봇 스트리밍 에러 ({bot_type})]: {e}", exc_info=True)  # exc_info로 트레이스백 포함
            error_payload = {"error_detail": "현재 서비스 이용이 원활하지 않습니다. 잠시 후 다시 시도해 주세요."}
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"

        finally:
            yield "data: [DONE]\n\n"
