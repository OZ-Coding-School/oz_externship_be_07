from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import QuestionCategories
from apps.users.models.models import User


class AdminCategoryTests(TestCase):
    admin_user: User
    parent_category: QuestionCategories
    url: str
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        # 슈퍼유저 생성
        cls.admin_user = User.objects.create_superuser(
            email="admin@admin.com", password="password123", birthday=date(1990, 1, 1)
        )
        # 실제 부모 카테고리 생성
        cls.parent_category = QuestionCategories.objects.create(name="기본 카테고리")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        self.url = "/api/v1/qna/admin/qna/categories/"

    def test_create_category_success(self) -> None:
        # [성공] 정상적인 카테고리 등록 확인
        data = {"name": "신규 카테고리", "parent": self.parent_category.id}
        response = self.client.post(self.url, data, format="json", follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_required_fields_missing(self) -> None:
        # [실패] 필수 입력값(name) 누락 시 400 에러 확인
        data = {"parent": self.parent_category.id}
        response = self.client.post(self.url, data, format="json", follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_parent_not_found(self) -> None:
        # [실패] 존재하지 않는 부모 ID 입력 시 404 에러 확인
        last_obj = QuestionCategories.objects.last()
        non_existent_id = (last_obj.id if last_obj else 0) + 9999

        data = {"name": "하위 카테고리", "parent": non_existent_id}
        response = self.client.post(self.url, data, format="json", follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
