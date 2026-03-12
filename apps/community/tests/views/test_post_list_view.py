from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post
from apps.users.models.models import User


class PostListAPIViewTest(TestCase):
    client: APIClient
    user: User
    category: PostCategory
    post: Post

    @classmethod
    def setUpTestData(cls) -> None:
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
            title="테스트 게시글 1번",
            content="게시글 본문입니다.",
            author=cls.user,
            category=cls.category,
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_post_list_returns_200(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_list_returns_expected_result_fields(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url)

        result = response.json()["results"][0]

        self.assertEqual(result["id"], self.post.id)
        self.assertEqual(result["author"]["id"], self.user.id)
        self.assertEqual(result["category_id"], self.category.id)
