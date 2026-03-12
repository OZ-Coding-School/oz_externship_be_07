from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post
from apps.users.models.models import User


class PostDetailAPIViewTest(TestCase):
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

    def test_get_post_detail_success(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["id"], self.post.id)
        self.assertEqual(data["author"]["id"], self.user.id)
        self.assertEqual(data["category"]["id"], self.category.id)

    def test_get_post_detail_not_found(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
