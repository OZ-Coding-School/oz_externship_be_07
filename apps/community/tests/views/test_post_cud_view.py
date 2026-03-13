from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post
from apps.users.models.models import User


class PostCreateUpdateDeleteViewTest(TestCase):
    client: APIClient
    user: User
    category: PostCategory
    post: Post

    def setUp(self) -> None:
        self.user = User.objects.create(
            email="test@test.com",
            password="password123",
            name="testuser",
            nickname="testuser",
            phone_number="01000000000",
            gender="M",
            birthday="2000-01-01",
        )
        self.category = PostCategory.objects.create(
            name="테스트 카테고리",
        )
        self.post = Post.objects.create(
            title="테스트 title",
            content="테스트 content",
            category=self.category,
            author=self.user,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_create_success(self) -> None:
        url = reverse("post-list")

        data = {
            "title": "테스트2 title",
            "content": "테스트2 content",
            "category": self.category.id,
            "author": self.user.id,
        }
        response = self.client.post(url, data)
        get_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_data["detail"], "게시글이 성공적으로 생성되었습니다.")
        self.assertIn("pk", get_data)

    def test_post_create_fail(self) -> None:
        url = reverse("post-list")

        data = {"content": "테스트2 content", "category": self.category.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_update_success(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        data = {"title": "테스트 수정 title", "content": "테스트 수정 content", "category": self.category.id}
        response = self.client.put(url, data, content_type="application/json")
        get_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["title"], data["title"])
        self.assertEqual(get_data["content"], data["content"])
        self.assertEqual(get_data["category_id"], self.category.id)

    def test_post_update_fail(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        data = {
            "title": "테스트 수정 title",
            "content": "테스트 수정 content",
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_delete_success(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        response = self.client.delete(url)
        get_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["detail"], "게시글이 삭제되었습니다.")

    def test_post_delete_fail(self) -> None:
        url = reverse("post-detail", kwargs={"post_id": 99})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
