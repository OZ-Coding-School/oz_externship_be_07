import json
import logging
from typing import Any, Iterator, cast

from django.conf import settings
from django.core.cache import cache
from google import genai

from apps.chatbot.choices import BotTypeChoices, ChatbotModelChoices, MessageRoleChoices
from apps.chatbot.prompts.support_context import SUPPORT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ChatbotService:
    SESSION_TTL = 3600

    @staticmethod
    def check_and_increment_limit(bot_type: str, session_id: str, user: Any) -> None:
        """
        QnA 챗봇에 질문한 횟수를 확인하고 1 증가 (최대 2회)
        """
        count_key = f"chatbot:{bot_type}:count:{session_id}"

        # print(f"\n🔍 [DEBUG] Checking Key: {count_key}")
        # print(f"🔍 [DEBUG] Current Value in Cache: {cache.get(count_key)}")

        current_count = int(cache.get(count_key, 0) or 0)

        if current_count >= 2:
            raise PermissionError("추가 질문은 2회까지 가능합니다. 새로운 질문글을 작성해 주세요.")

        cache.set(count_key, current_count + 1, timeout=ChatbotService.SESSION_TTL)

    @classmethod
    def get_ephemeral_history(cls, bot_type: str, session_id: str) -> list[dict[str, Any]]:
        """
        Redis에서 특정 세션의 대화 내역 조회
        """
        history_key = f"chatbot:{bot_type}:history:{session_id}"
        raw_history = cache.get(history_key)

        return cast(list[dict[str, Any]], raw_history or [])

    @classmethod
    def delete_ephemeral_session(cls, bot_type: str, session_id: str) -> None:
        """
        특정 봇 타입의 특정 세션 Redis 캐시 초기화
        """
        history_key = f"chatbot:{bot_type}:history:{session_id}"
        count_key = f"chatbot:{bot_type}:count:{session_id}"

        cache.delete(history_key)
        cache.delete(count_key)

    @staticmethod
    def _append_to_history(bot_type: str, session_id: str, role: str, message: str) -> None:
        """
        Redis 대화내역에 새로운 메시지 추가 (내부용)
        """
        history_key = f"chatbot:{bot_type}:history:{session_id}"
        history = cache.get(history_key, [])

        history.append({"role": role, "message": message})

        cache.set(history_key, history, timeout=ChatbotService.SESSION_TTL)

    @staticmethod
    def stream_ephemeral_response(
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
        client = genai.Client(api_key=api_key)

        ChatbotService._append_to_history(bot_type, session_id, MessageRoleChoices.USER, user_message)

        target_model = ChatbotModelChoices.GEMINI_2_0_FLASH_LITE_001.value
        system_instruction = "당신은 오즈코딩스쿨의 전문적인 프로그래밍 QnA 튜터입니다."

        if bot_type == BotTypeChoices.SUPPORT.value:
            system_instruction = SUPPORT_SYSTEM_PROMPT if SUPPORT_SYSTEM_PROMPT else "친절한 상담원입니다."
            target_model = ChatbotModelChoices.GEMINI_2_5_FLASH.value

        raw_history = ChatbotService.get_ephemeral_history(bot_type, session_id)
        formatted_contents: list[Any] = [
            {
                "role": "user" if msg["role"] == MessageRoleChoices.USER.value else "model",
                "parts": [{"text": msg["message"]}],
            }
            for msg in raw_history
        ]

        full_response = ""
        try:
            logger.info(f"Using Model: {target_model} for Bot Type: {bot_type}")

            response = client.models.generate_content_stream(
                model=target_model,
                contents=formatted_contents,
                config={"system_instruction": system_instruction, "temperature": 0.7},
            )

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    payload = {"role": MessageRoleChoices.ASSISTANT.value, "content": chunk.text}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"[챗봇 스트리밍 에러 ({bot_type})]: {e}")
            yield f"data: {json.dumps({'error_detail': f'AI 응답 생성 오류:{str(e)}'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        if full_response.strip():
            ChatbotService._append_to_history(bot_type, session_id, MessageRoleChoices.ASSISTANT.value, full_response)
        else:
            fallback_msg = "죄송합니다. 정책에 의해 차단되었거나, 답변을 생성하지 못했습니다."
            yield f"data: {json.dumps({'error_detail': fallback_msg}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        yield "data:[DONE]\n\n"
