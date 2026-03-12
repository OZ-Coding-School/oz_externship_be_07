from typing import Any

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.chatbot.models import ChatbotSessions
from apps.chatbot.serializers import (
    ChatbotSessionCreateSerializer,
    ChatbotSessionReadSerializer,
)
from apps.questions.models import QuestionCategories, Questions
from apps.users.models.models import User

from .choices import ChatbotModelChoices


class ChatbotSerializerTest(TestCase):
    user: User
    question: Questions
    category: QuestionCategories

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@test.com",
            password="testpassword123",
            name="테스트유저",
            nickname="테스트닉",
            phone_number="01012345678",
            gender="MALE",
            birthday="2000-01-01",
        )

        cls.category = QuestionCategories.objects.create()

        cls.question = Questions.objects.create(
            title="테스트 질문",
            content="내용",
            category_id=cls.category.id,  #
        )

    def test_create_serializer_valid(self) -> None:
        factory = APIRequestFactory()
        request = factory.post("/api/v1/chatbot/sessions/")
        request.user = self.user

        valid_data = {
            "question": self.question.id,
            "title": " Test 관련 심오한 질문",
            "using_model": ChatbotModelChoices.GEMINI_2_5_FLASH,
        }
        serializer = ChatbotSessionCreateSerializer(data=valid_data, context={"request": request})

        is_valid = serializer.is_valid()  # is_valid() 먼저 호출

        self.assertTrue(is_valid, msg=serializer.errors)

        session = serializer.save()

        self.assertEqual(session.user, self.user)

    def test_create_serializer_invalid(self) -> None:
        factory = APIRequestFactory()
        request = factory.post("/api/v1/chatbot/sessions/")
        request.user = self.user

        invalid_data = {
            "using_model": "gemini-2.5-flash"
        }  # question, title 누락된 경우// 경우의 수 생성하는 로직 괜찮겠다.

        serializer = ChatbotSessionCreateSerializer(data=invalid_data, context={"request": request})

        self.assertFalse(serializer.is_valid())
        self.assertIn("question", serializer.errors)
        self.assertIn("title", serializer.errors)

    def test_read_serializer_output(self) -> None:
        session = ChatbotSessions.objects.create(
            user=self.user, question=self.question, title="테스트 채팅방", using_model="gemini"
        )
        serializer = ChatbotSessionReadSerializer(instance=session)

        self.assertEqual(serializer.data["title"], "테스트 채팅방")
        self.assertEqual(serializer.data["question_id"], self.question.id)
        self.assertIn("created_at", serializer.data)
