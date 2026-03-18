from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post, PostLike

User = get_user_model()


class PostLikeAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            birthday=date(2000, 1, 1),
        )
        self.category = PostCategory.objects.create(name="테스트")
        self.post = Post.objects.create(
            author=self.user,
            category=self.category,
            title="테스트 게시글",
            content="내용",
        )
        self.url = reverse("post-detail", kwargs={"post_id": self.post.id})
        self.not_found_url = reverse("post-detail", kwargs={"post_id": 9999})

    def _login(self) -> None:
        self.client.force_authenticate(user=self.user)

    def _post_like(self, is_liked: bool, url: str | None = None) -> Response:
        return self.client.post(
            url or self.url,
            {"is_liked": is_liked},
            format="json",
        )

    def test_post_like_success(self) -> None:
        self._login()
        response = self._post_like(True)

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
        self._login()
        PostLike.objects.create(post=self.post, user=self.user, is_liked=True)

        response = self._post_like(False)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_liked"], False)
        self.assertEqual(response.data["like_count"], 0)

    def test_post_like_unauthorized(self) -> None:
        response = self._post_like(True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_like_not_found(self) -> None:
        self._login()
        response = self._post_like(True, self.not_found_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_like_invalid_request(self) -> None:
        self._login()
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_like_no_duplicate(self) -> None:
        self._login()
        self._post_like(True)
        self._post_like(True)

        count = PostLike.objects.filter(post=self.post, user=self.user).count()
        self.assertEqual(count, 1)
