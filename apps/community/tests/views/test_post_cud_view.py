from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post
from apps.users.models import User


class PostCreateUpdateDeleteViewTest(TestCase):
    user: User
    category: PostCategory
    post: Post

    @classmethod
    def setUp(cls) -> None:
        cls.user = User.objects.create(
            email="test@test.com",
            name="testuser",
            hashed_password="password123",
            birthday="2000-01-01",
        )
        cls.category = PostCategory.objects.create(
            name="테스트 카테고리",
        )
        cls.post = Post.objects.create(
            title="테스트 title",
            content="테스트 content",
            category=cls.category,
            author=cls.user,
        )

    def test_post_create_success(self) -> None:
        url = reverse("post_create")

        data = {
            "title": "테스트2 title",
            "content": "테스트2 content",
            "category": self.category.id,
            "author": self.user.id,
        }
        response = self.client.post(url, data)
        get_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["detail"], "게시글이 성공적으로 생성되었습니다.")
        self.assertIn("pk", get_data)

    def test_post_update_success(self) -> None:
        url = reverse("post_update", kwargs={"pk": self.post.id})
        data = {
            "title": "테스트 수정 title",
            "content": "테스트 수정 content",
            "category": self.category.id,
        }
        response = self.client.put(url, data)
        get_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["title"], data["title"])
        self.assertEqual(get_data["content"], data["content"])
        self.assertEqual(get_data["category_id"], self.category.id)

    def test_post_delete_success(self) -> None:
        url = reverse("post_delete", kwargs={"pk": self.post.id})
        response = self.client.delete(url)
        get_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["detail"], "게시글이 삭제되었습니다.")

    def test_post_delete_fail(self) -> None:
        url = reverse("post_delete", kwargs={"pk": 2})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
