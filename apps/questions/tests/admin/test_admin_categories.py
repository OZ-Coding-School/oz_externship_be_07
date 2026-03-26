from datetime import date
from typing import Any, Mapping, cast

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.questions.models import QuestionCategories, Questions
from apps.users.models.models import User


class AdminQuestionListTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email="admin_test@admin.com",
            password="password123",
            birthday=date(1990, 1, 1),
        )
        self.client.force_authenticate(user=self.admin_user)

        self.category = QuestionCategories.objects.create(name="테스트 카테고리")
        Questions.objects.create(
            author=self.admin_user, category=self.category, title="테스트 질문", content="테스트 내용"
        )

        try:
            self.url = reverse("admin_questions:admin_question_list")
        except Exception:
            self.url = "/api/v1/admin/qna/questions/"

    def test_get_question_list_full_coverage(self) -> None:
        params: Mapping[str, Any] = {
            "page": 1,
            "size": 10,
            "search_keyword": "테스트",
            "category_id": self.category.id,
            "answer_status": "unanswered",
            "sort": "oldest",
        }

        response = cast(Response, self.client.get(self.url, data=params, format="json"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.data
        self.assertEqual(res_data["page"], 1)
        self.assertEqual(res_data["search_keyword"], "테스트")
        self.assertEqual(int(res_data["category_id"]), self.category.id)
        self.assertEqual(res_data["answer_status"], "unanswered")
        self.assertEqual(res_data["sort"], "oldest")
