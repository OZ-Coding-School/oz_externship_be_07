from django.db import models


class ChatbotModelChoices(models.TextChoices):
    """
    LLM 모델 종류
    """

    GEMINI_1_5_FLASH = "gemini-1.5-flash", "Gemini 1.5 Flash"
    GEMINI_2_0 = "gemini-2.0", "Gemini 2.0"


class MessageRoleChoices(models.TextChoices):
    """
    챗봇 메시지 발화자
    """

    USER = "USER", "사용자"
    ASSISTANT = "ASSISTANT", "AI"
