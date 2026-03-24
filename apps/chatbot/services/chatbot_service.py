import json
import logging
from typing import Any, Iterator, cast

from django.core.cache import cache
from django.db.models import QuerySet
from google import genai

from apps.chatbot.choices import MessageRoleChoices, ChatbotModelChoices
from apps.chatbot.prompts.support_context import SUPPORT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ChatbotService:
    SESSION_TTL = 3600

    @staticmethod
    def check_and_increment_limit(session_id: str, user: Any) -> None:
        """
        QnA 챗봇에 질문한 횟수를 확인하고 1 증가 (최대 2회)
        """
        count_key = f"chatbot:count:{session_id}"

        current_count = cache.get(count_key, 0)

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
            - bot_type="qna": 기존 대화 내역 사용
            - bot_type="support": CS 전용 시스템 프롬프트 주입
        """
        client = genai.Client(api_key=api_key)
        
        if bot_type == "support":
            system_instruction = SUPPORT_SYSTEM_PROMPT if SUPPORT_SYSTEM_PROMPT else "친절한 고객지원 AI입니다."
        else:
            system_instruction = "당신은 오즈코딩스쿨의 QnA 도우미입니다."

        ChatbotService._append_to_history(bot_type, session_id, MessageRoleChoices.USER, user_message)
        raw_history = ChatbotService.get_ephemeral_history(bot_type, session_id)

        system_instruction = SUPPORT_SYSTEM_PROMPT if bot_type == "support" else "당신은 QnA 도우미입니다."

        formatted_history = "--- 대화 내역 ---\n"
        for msg in raw_history:
            role_label = "사용자" if msg["role"] == MessageRoleChoices.USER else "AI"
            formatted_history += f"{role_lable}:{msg['message']}\n"
        
            formatted_contents = []
            for msg in raw_history:
                formatted_contents.append({
                    "role": "user" if msg["role"] == MessageRoleChoices.USER.value else "model",
                    "parts": [{"text": msg["message"]}]
                })
        
        full_response = ""
        try:
            response = client.models.generate_content_stream(
                model=ChatbotModelChoices.GEMINI_1_5_FLASH.value,
                contents=user_message,
                config={"system_instruction": system_instruction, "temperature": 0.7},
            )
            
            for chunk in response:
                if chunk.text:
                    yield f"data: {json.dump({"rolr":MessageRoleChoices, "content": chunk.text}ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"[챗봇 스트리밍 에러 ({bot_type})]: {e}")
            error_msg = f"AI 답변 생성 중 오류가 발생했습니다: {str(e)}"
            yield f"data: {json.dumps({'error_detail': error_msg}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        if not full_response.strip():  # 빈 답변 방어
            fallback_msg = "죄송합니다. 정책에 의해 차단되었거나, 답변을 생성하지 못했습니다."
            yield f"data: {json.dumps({'error_detail': fallback_msg}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        ChatbotService._append_to_history(bot_type, session_id, MessageRoleChoices.ASSISTANT, full_response)

        yield "data:[DONE]\n\n"
