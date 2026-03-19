from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.questions.models import QuestionCategories, Questions
from apps.questions.services.questions_list_services import QuestionListService
from apps.users.models.models import User


class QuestionListTest(TestCase):
    api_client: APIClient
    cat1: QuestionCategories
    q1: Questions

    @classmethod
    def setUpTestData(cls) -> None:
        user = User.objects.create_user(
            email="listtest@test.com",
            name="조회테스트",
            nickname="조회용",
            phone_number="010-4251-4952",
            birthday="1999-05-29",
        )
        cls.cat1 = QuestionCategories.objects.create(name="백엔드")
        cls.q1 = Questions.objects.create(
            author=user, category=cls.cat1, title="백엔드 질문", content="백엔드는 어떤걸 의미하나요?"
        )

    def test_get_question_list_filtering(self) -> None:
        queryset: QuerySet[Questions] = QuestionListService.get_question_list(category_id=self.cat1.id)
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.q1, queryset)

    def test_get_question_detail_increment_view_count(self) -> None:
        initial_views: int = self.q1.view_count
        question: Questions = QuestionListService.get_question_detail(self.q1.id)

        self.assertEqual(question.view_count, initial_views + 1)

    def test_get_questions_invalid_category_id(self) -> None:
        url = reverse("questions:question-list")
        response: Response = self.api_client.get(url, {"category_id": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "유효하지 않은 카테고리 ID입니다.")

    def test_get_question_detail_not_found(self) -> None:
        url = reverse("questions:question-detail", kwargs={"question_id": 99999})
        response: Response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 질문입니다.")
