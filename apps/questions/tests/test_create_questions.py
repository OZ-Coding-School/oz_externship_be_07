from typing import List

from django.test import TestCase

from apps.questions.models import QuestionCategories, Questions
from apps.questions.services.questions_create_services import QuestionCreateService
from apps.users.choices import UserRole
from apps.users.models.models import User


class QuestionCreateTest(TestCase):
    category: QuestionCategories
    student: User
    teacher: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = QuestionCategories.objects.create(name="Django")
        cls.student = User.objects.create_user(
            email="test@test.com",
            password="pw1234",
            name="오즈",
            nickname="깡통",
            phone_number="010-1234-1234",
            birthday="2000-04-01",
            gender="MALE",
            role=UserRole.STUDENT,
        )
        cls.teacher = User.objects.create_user(
            email="testuser@test.com",
            password="pw1234",
            name="백엔드",
            nickname="프론트",
            phone_number="010-5678-1234",
            birthday="2000-04-01",
            gender="MALE",
            role=UserRole.TA,
        )

    def test_create_question_success(self) -> None:
        image_urls: List[str] = ["http://test.com/img1.png"]

        question: Questions = QuestionCreateService.create_question(
            user=self.student,
            category_id=self.category.id,
            title="이것은 테스트입니다.",
            content="테스트 코드 작성 어렵다.",
            image_url_list=image_urls,
        )
        self.assertEqual(Questions.objects.count(), 1)
