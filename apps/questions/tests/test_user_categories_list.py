from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import QuestionCategories
from apps.users.models.models import User


class UserCategoryListTest(TestCase):
    client: APIClient
    user: User
    url: str
    student: User
    parent_category: QuestionCategories
    child_category: QuestionCategories

    @classmethod
    def setUpTestData(cls) -> None:

        cls.student = User.objects.create_user(
            email="test@test.com",
            password="pw1234",
            name="김오즈",
            nickname="백학습",
            phone_number="010-1234-1234",
            gender="MALE",
            birthday=date(2000, 3, 22),
            role="STUDENT",
        )
        cls.user = User.objects.create_user(
            email="user@user.com",
            password="pw1234",
            name="방문객",
            nickname="배울까",
            phone_number="010-4321-3214",
            gender="MALE",
            birthday=date(2001, 5, 11),
            role="USER",
        )

        cls.parent_category = QuestionCategories.objects.create(name="백엔드")
        cls.child_category = QuestionCategories.objects.create(name="Python", parent=cls.parent_category)
        cls.url = reverse("questions:categories")

    def setUp(self) -> None:
        self.client = APIClient()

    # 성공 테스트
    def test_get_category_list_success(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("categories", response.data)

    # 로그인 인증 실패
    def test_get_category_list_unauthorized(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 조회 권한 실패
    def test_get_category_list_permission_denied(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
