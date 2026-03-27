from datetime import date
from typing import Any, ClassVar

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post, PostLike

User = get_user_model()


class PostLikeAPIViewTest(APITestCase):
    user: ClassVar[Any]
    category: ClassVar[PostCategory]
    post: ClassVar[Post]
    url: ClassVar[str]
    not_found_url: ClassVar[str]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            birthday=date(2000, 1, 1),
        )
        cls.category = PostCategory.objects.create(name="테스트")
        cls.post = Post.objects.create(
            author=cls.user,
            category=cls.category,
            title="테스트 게시글",
            content="내용",
        )
        cls.url = reverse("post-like", kwargs={"post_id": cls.post.id})
        cls.not_found_url = reverse("post-like", kwargs={"post_id": 9999})

    def _login(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_post_like_success(self) -> None:
        self._login()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_liked"], True)
        self.assertEqual(response.data["like_count"], 1)
        self.assertTrue(
            PostLike.objects.filter(
                post=self.post,
                user=self.user,
                is_liked=True,
            ).exists()
        )

    def test_post_unlike_success(self) -> None:
        PostLike.objects.create(post=self.post, user=self.user, is_liked=True)
        self._login()

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_liked"], False)
        self.assertEqual(response.data["like_count"], 0)

    def test_post_like_unauthorized(self) -> None:
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_like_not_found(self) -> None:
        self._login()
        response = self.client.post(self.not_found_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_like_no_duplicate(self) -> None:
        self._login()
        self.client.post(self.url)
        self.client.post(self.url)

        count = PostLike.objects.filter(post=self.post, user=self.user).count()
        self.assertEqual(count, 1)
