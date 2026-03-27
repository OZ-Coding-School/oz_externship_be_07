from django.db import models


class ChatbotModelChoices(models.TextChoices):
    """
    LLM 모델 종류
    """

    GEMINI_2_0_FLASH = "gemini-2.0-flash", "Gemini 2.0 Flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash", "Gemini 2.5 Flash"
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite"


class MessageRoleChoices(models.TextChoices):
    """
    챗봇 메시지 발화자
    """

    USER = "user", "사용자"
    ASSISTANT = "assistant", "AI"
