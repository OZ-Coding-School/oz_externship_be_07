from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


class ChatbotSessions(TimeStampModel):
    class ModelChoices(models.TextChoices):
        GEMINI_1_5_FLASH = "gemini-1.5-flash", "Gemini 1.5 Flash"
        GEMINI_2_0 = "gemini-2.0", "Gemini 2.0"
        # 필요에 따라 추가 (예: gemini-2.5-flash)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chatbot_sessions",
        help_text="채팅을 시작한 유저 ID",
    )

    question = models.ForeignKey(
        "question.Questions",  # 'Questions' 모델이 정의되어 있어야 함
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chatbot_sessions",
        help_text="파생된 Q&A 질문 ID",
    )

    title = models.CharField(max_length=30, null=False, help_text="AI가 요약한 세션 제목")

    using_model = models.CharField(max_length=50, choices=ModelChoices.choices, null=False, help_text="LLM 사용 모델")

    class Meta:
        db_table = "chatbot_sessions"
        verbose_name = "챗봇 세션"
        unique_together = (("user", "question"),)  # user_id와 question_id 조합으로 유니크 설정


class ChatbotCompletions(TimeStampModel):
    class RoleChoices(models.TextChoices):
        USER = "USER", "사용자"
        ASSISTANT = "ASSISTANT", "AI"

    session = models.ForeignKey(
        ChatbotSessions,
        on_delete=models.CASCADE,
        related_name="completions",
        help_text="소속된 대화 세션 ID",
    )

    message = models.TextField(null=False, help_text="챗봇과의 채팅내용")

    role = models.CharField(
        max_length=10, choices=RoleChoices.choices, null=False, help_text="USER(사용자) 또는 ASSISTANT(AI) 구분"
    )

    class Meta:
        db_table = "chatbot_completions"
        verbose_name = "챗봇 메시지"
