from datetime import date
from typing import Any

from django.test import TestCase
from django.urls import reverse
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
        cls.admin_user = User.objects.create_superuser(
            email="admin@admin.com",
            password="password123",
            birthday=date(1990, 1, 1),
        )
        cls.parent_category = QuestionCategories.objects.create(name="기본 카테고리")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        try:
            self.url = reverse("admin_questions:admin_category_create")
        except Exception:
            self.url = "/api/v1/admin/qna/categories/"

    def test_create_category_success(self) -> None:
        """[성공] 정상적인 카테고리 등록 확인"""
        data: dict[str, Any] = {
            "name": "신규 카테고리",
            "category_type": "medium",
            "parent_id": self.parent_category.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_required_fields_missing(self) -> None:
        """[실패] 필수 입력값(name) 누락 시 400 에러 확인"""
        data: dict[str, Any] = {
            "category_type": "medium",
            "parent_id": self.parent_category.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_parent_not_found(self) -> None:
        """[실패] 존재하지 않는 부모 ID 입력 시 404 에러 확인"""
        non_existent_id = self.parent_category.id + 9999
        data: dict[str, Any] = {
            "name": "하위 카테고리",
            "category_type": "small",
            "parent_id": non_existent_id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_category_duplicate_name(self) -> None:
        """[실패] 동일한 부모 아래 동일한 이름 존재 시 409 에러 확인"""
        data: dict[str, Any] = {
            "name": "기본 카테고리",
            "category_type": "large",
            "parent_id": None,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
