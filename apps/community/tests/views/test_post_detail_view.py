from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post, PostLike
from apps.users.models.models import User


class PostDetailAPIViewTest(TestCase):
    client: APIClient
    user: User
    category: PostCategory
    inactive_category: PostCategory
    post: Post
    hidden_post: Post
    inactive_category_post: Post

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            email="test@test.com",
            name="testuser",
            password="password123",
            birthday="2000-01-01",
        )

        cls.category = PostCategory.objects.create(
            name="테스트 카테고리",
        )

        cls.inactive_category = PostCategory.objects.create(
            name="비활성 카테고리",
            status=False,
        )

        cls.post = Post.objects.create(
            title="테스트 게시글 1번",
            content="게시글 본문입니다.",
            author=cls.user,
            category=cls.category,
            view_count=3,
        )

        cls.hidden_post = Post.objects.create(
            title="숨김 게시글",
            content="숨김 본문입니다.",
            author=cls.user,
            category=cls.category,
            is_visible=False,
        )

        cls.inactive_category_post = Post.objects.create(
            title="비활성 카테고리 게시글",
            content="비활성 카테고리 본문입니다.",
            author=cls.user,
            category=cls.inactive_category,
        )

        PostLike.objects.create(
            user=cls.user,
            post=cls.post,
            is_liked=True,
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_post_detail_success(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["id"], self.post.id)
        self.assertEqual(data["title"], self.post.title)
        self.assertEqual(data["content"], self.post.content)
        self.assertEqual(data["author"]["id"], self.user.id)
        self.assertEqual(data["category"]["id"], self.category.id)
        self.assertEqual(data["category"]["name"], self.category.name)

        self.assertIn("view_count", data)
        self.assertIn("like_count", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_get_post_detail_not_found(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "게시글을 찾을 수 없습니다.")

    def test_get_post_detail_returns_404_when_post_is_invisible(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": self.hidden_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "게시글을 찾을 수 없습니다.")

    def test_get_post_detail_returns_404_when_category_is_inactive(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": self.inactive_category_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "게시글을 찾을 수 없습니다.")
