from typing import Any, Mapping, cast

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.questions.models import Answers, QuestionCategories, Questions
from apps.users.models.models import User


class AdminQuestionListTests(TestCase):
    category: QuestionCategories
    parent_category: QuestionCategories
    question: Questions
    url: str
    admin_user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = QuestionCategories.objects.create(name="테스트 카테고리")
        cls.url = reverse("admin_questions:admin-question-list")
        cls.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="admin123",
            name="testadmin",
            nickname="testadmin",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1970-01-01",
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
        )

        # 임의의 카테고리 생성
        cls.parent_category = QuestionCategories.objects.create(name="테스트")
        cls.category = QuestionCategories.objects.create(name="백엔드", parent=cls.parent_category)

        # 임의의 질문 생성
        cls.question = Questions.objects.create(
            title="Test Question",
            content="test cotent 50 넘어야 프리뷰 로직이 실행. " * 5,
            author=cls.admin_user,
            category=cls.category,
        )

        # 답변 생성
        Answers.objects.create(
            questions=cls.question,
            author=cls.admin_user,
            content="Test Answer",
        )

        cls.url = reverse("admin_questions:admin-question-list")

    def test_get_question_list_full_coverage(self) -> None:
        client = APIClient()
        client.force_authenticate(user=self.admin_user)
        params: Mapping[str, Any] = {
            "page": 1,
            "size": 10,
            "search_keyword": "테스트",
            "category_id": self.category.id,
            "answer_status": "unanswered",
            "sort": "oldest",
        }

        response = cast(Response, client.get(self.url, data=params, format="json"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.data
        self.assertEqual(res_data["page"], 1)
        self.assertEqual(res_data["size"], 10)
        self.assertIn("total_count", res_data)
        self.assertIn("questions", res_data)
