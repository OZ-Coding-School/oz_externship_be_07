from django.test import TestCase
# from apps.users.models.models import User
from typing import Any
from .choices import ChatbotModelChoices
from apps.questions.models import Questions, QuestionCategories
from apps.chatbot.models import ChatbotSessions
from apps.chatbot.serializers import ChatbotSessionCreateSerializer, ChatbotSessionReadSerializer


class ChatbotSerializerTest(TestCase):
    user: Any
    question: Questions
    category: QuestionCategories
    
    @classmethod
    def setUpTestData(cls) -> None:
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        cls.user = UserModel.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="123",
            first_name="xptmx"
            # gender="MALE"
        )
        
        cls.category = QuestionCategories.objects.create(
        )
        
        cls.question = Questions.objects.create(
            title="테스트 질문",
            content="내용",
            category_id=cls.category.id
        )
        
    def test_create_serializer_valid(self):
        valid_data = {
            "user" : self.user.id,
            "question" : self.question.id,
            "title" : " Test 관련 심오한 질문",
            "using_model" : ChatbotModelChoices.GEMINI_2_5_FLASH
        }
        serializer = ChatbotSessionCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        
    def test_create_serializer_invalid(self):
        invalid_data = {
            "user": self.user.id,
            "using_model": "gemini-2.5-flash"
        }
        serializer = ChatbotSessionCreateSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('question', serializer.errors)
        self.assertIn('title', serializer.errors)
        
    def test_read_serializer_output(self):
        session = ChatbotSessions.objects.create(
            user=self.user,
            question=self.question,
            title="테스트 채팅방",
            using_model="gemini"
        )
        serializer = ChatbotSessionReadSerializer(instance=session)
        
        self.assertEqual(serializer.data["title"], "테스트 채팅방")
        self.assertEqual(serializer.data["question_id"], self.question.id)
        self.assertIn("created_at", serializer.data)