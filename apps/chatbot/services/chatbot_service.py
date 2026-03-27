from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Iterator, cast

from django.conf import settings
from django.core.cache import caches
from django.db.models import QuerySet
from google import genai

from apps.chatbot.choices import ChatbotModelChoices, MessageRoleChoices
from apps.chatbot.exceptions import (
    ChatbotThrottledError,
    CompletionLimitExceededError,
    SessionNotFoundError,
)
from apps.chatbot.models import ChatbotCompletions, ChatbotSessions
from apps.chatbot.prompts.question_prompts import QUESTION_SYSTEM_PROMPT
from apps.chatbot.prompts.support_context import SUPPORT_FULL_PROMPT
from apps.chatbot.services.question_completion_policy import validate_question_input
from apps.chatbot.services.support_completion_policy import validate_support_input

if TYPE_CHECKING:
    from apps.users.models.models import User

chatbot_cache = caches["chatbot"]
logger = logging.getLogger(__name__)

MAX_QNA_QUESTIONS = 3


class ChatbotService:

    # ── QnA 세션 CRUD ──

    @classmethod
    def create_session(cls, user: User, question_id: int) -> tuple[ChatbotSessions, bool]:
        """QnA 세션 생성 또는 기존 세션 반환"""
        from apps.questions.models import Questions

        Questions.objects.get(id=question_id)

        session, created = ChatbotSessions.objects.get_or_create(
            user=user,
            question_id=question_id,
            defaults={
                "title": "새 질문",
                "using_model": ChatbotModelChoices.GEMINI_2_5_FLASH_LITE.value,
            },
        )
        return session, created

    @classmethod
    def get_user_sessions(cls, user: User) -> QuerySet[ChatbotSessions]:
        """유저의 챗봇 세션 목록 조회 (최신순)"""
        return ChatbotSessions.objects.filter(user=user).order_by("-created_at")

    @classmethod
    def get_session_detail(cls, session_id: int, user: User) -> ChatbotSessions:
        """유저의 단일 세션 조회"""
        try:
            return ChatbotSessions.objects.prefetch_related("completions").get(id=session_id, user=user)
        except ChatbotSessions.DoesNotExist:
            raise SessionNotFoundError("접근 권한이 없거나, 존재하지 않는 세션입니다.")

    @classmethod
    def delete_session(cls, session_id: int, user: User) -> None:
        """세션 삭제 (Cascade로 대화내역 함께 삭제)"""
        session = cls.get_session_detail(session_id, user)
        session.delete()

    @classmethod
    def get_session_completions(cls, session_id: int, user: User) -> QuerySet[ChatbotCompletions]:
        """세션의 대화내역 조회"""
        session = cls.get_session_detail(session_id, user)
        return session.completions.all().order_by("created_at")

    # ── QnA 사전 검증 (generator 밖에서 호출) ──

    @classmethod
    def validate_qna_request(cls, session_id: int, user_message: str) -> None:
        """QnA 요청 사전 검증 — generator 생성 전에 호출해야 함"""
        # 입력 검증 (프롬프트 인젝션 + 도메인 필터링)
        validate_question_input(user_message)

        # 세션 존재 확인
        try:
            session = ChatbotSessions.objects.get(id=session_id)
        except ChatbotSessions.DoesNotExist:
            raise SessionNotFoundError("챗봇 세션이 존재하지 않습니다.")

        # 질문 횟수 체크
        user_message_count = session.completions.filter(role=MessageRoleChoices.USER).count()
        if user_message_count >= MAX_QNA_QUESTIONS:
            raise CompletionLimitExceededError("더 심도있는 질문은 질문 게시판을 이용해주세요.")

        # Redis Lock 체크
        lock_key = f"chatbot:responding:{session_id}"
        if chatbot_cache.get(lock_key):
            raise ChatbotThrottledError("AI가 아직 이전 질문에 답변중입니다. 잠시 후 다시 시도해주세요.")

    # ── QnA 스트리밍 ──

    @classmethod
    def stream_qna_response(cls, session_id: int, user_message: str) -> Iterator[str]:
        """QnA 챗봇 SSE 스트리밍 — validate_qna_request를 먼저 호출할 것"""

        api_key = getattr(settings, "GEMINI_API_KEY", "")
        client = genai.Client(api_key=api_key)

        # Redis Lock 설정
        lock_key = f"chatbot:responding:{session_id}"
        chatbot_cache.set(lock_key, True, timeout=180)

        try:
            session = ChatbotSessions.objects.select_related("question").get(id=session_id)

            # 유저 메시지 저장
            ChatbotCompletions.objects.create(
                session=session,
                message=user_message,
                role=MessageRoleChoices.USER,
            )

            # 06기 프롬프트 + 질문 컨텍스트 주입
            question = session.question
            question_title = question.title if question else "일반 프로그래밍 질문"
            question_content = question.content if question else ""
            category_name = question.category.name if question and question.category else "기타"

            system_instruction = (
                f"{QUESTION_SYSTEM_PROMPT}\n\n"
                f"--- 현재 질문 컨텍스트 ---\n"
                f"질문 제목: {question_title}\n"
                f"카테고리: {category_name}\n"
                f"질문 내용: {question_content}"
            )

            # 이전 대화 내역
            history_qs = session.completions.all().order_by("created_at")
            formatted_contents = [
                {
                    "role": "user" if row.role == MessageRoleChoices.USER else "model",
                    "parts": [{"text": row.message}],
                }
                for row in history_qs
            ]

            # AI 스트리밍
            response = client.models.generate_content_stream(
                model=session.using_model,
                contents=cast(list[Any], formatted_contents),
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                },
            )

            # SSE 포맷으로 yield
            final_ai_message = ""
            for chunk in response:
                if chunk.text:
                    final_ai_message += chunk.text
                    yield f'data: {json.dumps({"content": chunk.text}, ensure_ascii=False)}\n\n'

            yield "data: [DONE]\n\n"

            # AI 응답 저장
            ChatbotCompletions.objects.create(
                session=session,
                message=final_ai_message,
                role=MessageRoleChoices.ASSISTANT,
            )

        except (CompletionLimitExceededError, ChatbotThrottledError, SessionNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Chatbot QnA Error: {e}")
            raise

        finally:
            chatbot_cache.delete(lock_key)

    # ── Support 사전 검증 ──

    @classmethod
    def validate_support_request(cls, user_message: str) -> None:
        """CS 상담 요청 사전 검증 — generator 생성 전에 호출해야 함"""
        validate_support_input(user_message)

    # ── Support (Stateless) 스트리밍 ──

    @classmethod
    def stream_support_response(cls, user_message: str) -> Iterator[str]:
        """CS 상담 전용 1회성 SSE 스트리밍 (세션 저장 없음)"""

        api_key = getattr(settings, "GEMINI_API_KEY", "")
        client = genai.Client(api_key=api_key)

        formatted_contents = [{"role": "user", "parts": [{"text": user_message}]}]

        response = client.models.generate_content_stream(
            model=ChatbotModelChoices.GEMINI_2_5_FLASH.value,
            contents=cast(list[Any], formatted_contents),
            config={"system_instruction": SUPPORT_FULL_PROMPT, "temperature": 0.7},
        )

        for chunk in response:
            if chunk.text:
                yield f'data: {json.dumps({"content": chunk.text}, ensure_ascii=False)}\n\n'

        yield "data: [DONE]\n\n"
