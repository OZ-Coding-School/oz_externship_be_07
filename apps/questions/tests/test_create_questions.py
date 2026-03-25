from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import QuestionCategories, Questions
from apps.users.choices import UserRole
from apps.users.models.models import User


class QuestionCreateTest(TestCase):
    large_category: QuestionCategories
    medium_category: QuestionCategories
    small_category: QuestionCategories
    student: User
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.large_category = QuestionCategories.objects.create(name="백엔드", parent=None)
        cls.medium_category = QuestionCategories.objects.create(name="Django", parent=cls.large_category)
        cls.small_category = QuestionCategories.objects.create(name="ORM", parent=cls.medium_category)
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
        cls.url = reverse("questions:question_list_create")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

    # 질문 등록 성공 코드
    def test_create_question_view_success(self) -> None:
        self.client.force_login(user=self.student)
        data = {
            "category_id": self.small_category.id,
            "title": "Test Title",
            "content": "test content",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Questions.objects.count(), 1)

    # 대분류 선택만 하고 ValueError 발생
    def test_create_question_view_fail_category(self) -> None:
        self.client.force_login(user=self.student)
        data = {
            "category_id": self.large_category.id,
            "title": "Fail Test",
            "content": "중분류, 소분류도 선택해주셔야 합니다.",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data if hasattr(response, "data") else response.json())

    # serializer 검증실패
    def test_create_view_validation_error(self) -> None:
        self.client.force_login(user=self.student)
        data = {"title": "필수 필드 누락 데이터"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
