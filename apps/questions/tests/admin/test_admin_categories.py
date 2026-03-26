from typing import Any, Mapping, cast

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.questions.models import QuestionCategories
from apps.users.models.models import User


class AdminQuestionListTests(TestCase):
    category: QuestionCategories
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
