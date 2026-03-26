from typing import Any, Mapping, cast

from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from apps.questions.models import QuestionCategories  # 모델 임포트 확인


class AdminQuestionListTests(APITestCase):
    category: QuestionCategories
    url: str

    def setUp(self) -> None:
        self.category = QuestionCategories.objects.create(name="테스트 카테고리")
        self.url = reverse("admin_questions:admin_question_list")

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
        self.assertEqual(res_data["size"], 10)
        self.assertIn("total_count", res_data)
        self.assertIn("questions", res_data)
