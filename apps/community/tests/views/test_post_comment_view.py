from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.community.models import PostComment
from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post
from apps.users.models.models import User


class PostCommentAPIViewTest(TestCase):
    client: APIClient
    user: User
    category: PostCategory
    post: Post
    comment: PostComment

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            email="test@test.com",
            name="test",
            nickname="test",
            hashed_password="qwer1234",
            birthday="1995-01-01",
            gender="M",
        )
        cls.user.save()

        cls.category = PostCategory.objects.create(name="테스트 카테고리")
        cls.post = Post.objects.create(
            title="테스트 게시글",
            content="테스트",
            author=cls.user,
            category=cls.category,
        )

        cls.comment = PostComment.objects.create(post=cls.post, author=cls.user, content="테스트 댓글")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_comment_list_returns_200(self) -> None:
        url = reverse("post-comment-list", kwargs={"post_id": self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comment_list_returns_expected_fields(self) -> None:
        url = reverse("post-comment-list", kwargs={"post_id": self.post.id})
        response = self.client.get(url)

        data = response.json()
        result = data["results"][0]
        print(f"data: {data}")
        print(f"result: {result}")

        self.assertEqual(data["count"], 1)
        self.assertEqual(result["content"], self.comment.content)
        self.assertEqual(result["author"], self.user.id)

    def test_create_comment_returns_201(self) -> None:
        self.client.force_authenticate(user=self.user)  # type: ignore

        url = reverse("post-comment-list", kwargs={"post_id": self.post.id})
        data = {"content": "로그인후 작성 테스트 댓글"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["detail"], "댓글이 등록되었습니다.")

        print(f"count: {PostComment.objects.count()}")
        self.assertEqual(PostComment.objects.count(), 2)

    def test_create_comment_anonymous_returns_401(self) -> None:
        url = reverse("post-comment-list", kwargs={"post_id": self.post.id})
        data = {"content": "로그인없이 작성 댓글"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
