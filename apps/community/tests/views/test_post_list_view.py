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
        cls.user = User.objects.create_user(
            email="test@test.com",
            password="password123",
            name="testuser",
            nickname="testuser",
            phone_number="01000000000",
            gender="M",
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)

        result = data["results"][0]

        self.assertEqual(result["id"], self.post.id)
        self.assertEqual(result["author"]["id"], self.user.id)
        self.assertEqual(result["category_name"], self.category.name)
        self.assertEqual(result["title"], self.post.title)

        self.assertIn("thumbnail_img_url", result)
        self.assertIn("content_preview", result)
        self.assertIn("comment_count", result)
        self.assertIn("view_count", result)
        self.assertIn("like_count", result)
        self.assertIn("created_at", result)
        self.assertIn("updated_at", result)
