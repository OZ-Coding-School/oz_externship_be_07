from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.community.models.category_model import PostCategory


class PostCategoryAPIViewTest(TestCase):
    client: APIClient
    active1: PostCategory
    active2: PostCategory
    inactive: PostCategory

    @classmethod
    def setUpTestData(cls) -> None:
        cls.active1 = PostCategory.objects.create(name="공지사항", status=True)
        cls.active2 = PostCategory.objects.create(name="자유게시판", status=True)
        cls.inactive = PostCategory.objects.create(name="숨김 카테고리", status=False)

    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_categories_returns_200(self) -> None:
        response = self.client.get(reverse("post-category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_categories_returns_only_active(self) -> None:
        response = self.client.get(reverse("post-category-list"))
        data = response.json()

        self.assertEqual(len(data), 2)
        names = [item["name"] for item in data]
        self.assertIn(self.active1.name, names)
        self.assertIn(self.active2.name, names)
        self.assertNotIn(self.inactive.name, names)

    def test_get_categories_sorted_by_id(self) -> None:
        response = self.client.get(reverse("post-category-list"))
        data = response.json()

        ids = [item["id"] for item in data]
        self.assertEqual(ids, sorted(ids))
