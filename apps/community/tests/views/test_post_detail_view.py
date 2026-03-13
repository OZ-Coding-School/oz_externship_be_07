from typing import Any

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
            email="detail@test.com",
            name="detailuser",
            nickname="detail01",
            phone_number="01055556666",
            gender="M",
            password="password123",
            birthday="2000-01-01",
        )
        cls.category = PostCategory.objects.create(name="테스트 카테고리")
        cls.inactive_category = PostCategory.objects.create(name="비활성 카테고리", status=False)
        cls.post = Post.objects.create(
            title="테스트 게시글 1번",
            content="게시글 본문입니다.",
            author=cls.user,
            category=cls.category,
            view_count=3,
        )
        cls.hidden_post = Post.objects.create(
            title="숨김 게시글", content="숨김 본문입니다.", author=cls.user, category=cls.category, is_visible=False
        )
        cls.inactive_category_post = Post.objects.create(
            title="비활성 카테고리 게시글",
            content="비활성 카테고리 본문입니다.",
            author=cls.user,
            category=cls.inactive_category,
        )
        PostLike.objects.create(user=cls.user, post=cls.post, is_liked=True)

    def setUp(self) -> None:
        self.client = APIClient()

    def _get(self, post_id: int) -> Any:
        return self.client.get(reverse("post-detail", kwargs={"post_id": post_id}))

    def test_get_post_detail_success(self) -> None:
        response = self._get(self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], self.post.id)
        self.assertEqual(data["title"], self.post.title)
        self.assertEqual(data["content"], self.post.content)
        self.assertEqual(data["author"]["id"], self.user.id)
        self.assertEqual(data["category"]["id"], self.category.id)
        self.assertEqual(data["category"]["name"], self.category.name)
        for field in ("view_count", "like_count", "created_at", "updated_at"):
            self.assertIn(field, data)

    def test_get_post_detail_not_found(self) -> None:
        response = self._get(999999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "게시글을 찾을 수 없습니다.")

    def test_get_post_detail_returns_404_when_post_is_invisible(self) -> None:
        response = self._get(self.hidden_post.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "게시글을 찾을 수 없습니다.")

    def test_get_post_detail_returns_404_when_category_is_inactive(self) -> None:
        response = self._get(self.inactive_category_post.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "게시글을 찾을 수 없습니다.")

    def test_post_update_success(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        data = {"title": "테스트 수정 title", "content": "테스트 수정 content", "category": self.category.id}
        response = self.client.put(url, data, content_type="application/json")
        get_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["title"], data["title"])
        self.assertEqual(get_data["content"], data["content"])
        self.assertEqual(get_data["category_id"], self.category.id)

    def test_post_update_fail(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        data = {
            "title": "테스트 수정 title",
            "content": "테스트 수정 content",
        }
        response = self.client.put(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_delete_success(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        response = self.client.delete(url)
        get_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["detail"], "게시글이 삭제되었습니다.")

    def test_post_delete_fail(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse("post-detail", kwargs={"post_id": 99})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
