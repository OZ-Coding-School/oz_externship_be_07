from typing import Any, Mapping, cast

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.questions.models import Answers, QuestionCategories, Questions
from apps.questions.serializers.admin.admin_qna_questions_serializers import (
    AdminQuestionListSerializer,  # 추가
)
from apps.users.models.models import User


class AdminQuestionListTests(TestCase):
    category: QuestionCategories
    parent_category: QuestionCategories
    question: Questions
    url: str
    admin_user: User

    @classmethod
    def setUpTestData(cls) -> None:
        # 1. 관리자 생성
        cls.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="admin123",
            name="test",
            nickname="test",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1970-01-01",
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
        )

        cls.parent_category = QuestionCategories.objects.create(name="부모")
        cls.category = QuestionCategories.objects.create(name="자식", parent=cls.parent_category)

        cls.question = Questions.objects.create(
            title="Test Question",
            content="이 본문은 50자가 확실히 넘어야 시리얼라이저의 프리뷰 로직이 실행됩니다. " * 10,
            author=cls.admin_user,
            category=cls.category,
        )

        Answers.objects.create(
            questions=cls.question,
            author=cls.admin_user,
            content="Test Answer",
        )
        cls.url = reverse("admin_questions:admin-question-list")

    def test_get_question_list_full_coverage(self) -> None:
        client = APIClient()
        client.force_authenticate(user=self.admin_user)

        params_answered: Mapping[str, Any] = {
            "page": 1,
            "size": 10,
            "search_keyword": "Test",
            "answer_status": "answered",
            "sort": "latest",
        }
        client.get(self.url, data=params_answered, format="json")

        params_unanswered: Mapping[str, Any] = {
            "page": 1,
            "size": 10,
            "answer_status": "unanswered",
            "sort": "oldest",
        }
        response = cast(Response, client.get(self.url, data=params_unanswered, format="json"))

        serializer = AdminQuestionListSerializer(instance=self.question)
        _ = serializer.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("questions", response.data)
