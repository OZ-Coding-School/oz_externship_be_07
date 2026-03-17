from django.db.models import QuerySet
from django.test import TestCase

from apps.questions.models import QuestionCategories, Questions
from apps.questions.services.questions_list_services import QuestionListService
from apps.users.models.models import User


class QuestionListTest(TestCase):
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
