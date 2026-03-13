from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.community.models.category_model import PostCategory
from apps.community.models.comment_model import PostComment
from apps.community.models.post_model import Post, PostImage, PostLike
from apps.users.models.models import User


class PostListAPIViewTest(TestCase):
    client: APIClient
    user: User
    other_user: User
    category: PostCategory
    other_category: PostCategory
    post: Post
    other_post: Post
    hidden_post: Post

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            email="test@test.com",
            name="testuser",
            nickname="testuser1",
            phone_number="01011112222",
            gender="M",
            password="password123",
            birthday="2000-01-01",
        )

        cls.other_user = User.objects.create(
            email="other@test.com",
            name="otheruser",
            nickname="otheruser1",
            phone_number="01033334444",
            gender="F",
            password="password123",
            birthday="2000-01-02",
        )

        cls.category = PostCategory.objects.create(
            name="테스트 카테고리",
        )

        cls.other_category = PostCategory.objects.create(
            name="자유게시판",
        )

        cls.post = Post.objects.create(
            title="테스트 게시글 1번",
            content="게시글 본문입니다.",
            author=cls.user,
            category=cls.category,
            view_count=5,
        )

        cls.other_post = Post.objects.create(
            title="자유게시판 글",
            content="다른 게시글 본문입니다.",
            author=cls.other_user,
            category=cls.other_category,
            view_count=10,
        )

        cls.hidden_post = Post.objects.create(
            title="숨김 게시글",
            content="보이면 안 되는 게시글입니다.",
            author=cls.user,
            category=cls.category,
            is_visible=False,
        )

        PostImage.objects.create(
            post=cls.post,
            img_url="https://example.com/image1.png",
        )

        PostComment.objects.create(
            author=cls.other_user,
            post=cls.post,
            content="댓글입니다.",
        )

        PostLike.objects.create(
            user=cls.other_user,
            post=cls.post,
            is_liked=True,
        )

        PostLike.objects.create(
            user=cls.user,
            post=cls.other_post,
            is_liked=True,
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

        self.assertEqual(result["id"], self.other_post.id)
        self.assertEqual(result["author"]["id"], self.other_user.id)
        self.assertEqual(result["category_name"], self.other_category.name)
        self.assertEqual(result["title"], self.other_post.title)

        self.assertIn("thumbnail_img_url", result)
        self.assertIn("content_preview", result)
        self.assertIn("comment_count", result)
        self.assertIn("view_count", result)
        self.assertIn("like_count", result)
        self.assertIn("created_at", result)
        self.assertIn("updated_at", result)

    def test_get_post_list_excludes_invisible_post(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        result_ids = [result["id"] for result in results]

        self.assertIn(self.post.id, result_ids)
        self.assertIn(self.other_post.id, result_ids)
        self.assertNotIn(self.hidden_post.id, result_ids)

    def test_get_post_list_with_category_filter_success(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url, {"category_id": self.category.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.post.id)
        self.assertEqual(data["results"][0]["category_name"], self.category.name)

    def test_get_post_list_with_category_filter_no_result(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url, {"category_id": 999999})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])

    def test_get_post_list_with_author_search(self) -> None:
        url = reverse("post-list")
        response = self.client.get(
            url,
            {
                "search": self.user.nickname,
                "search_filter": "author",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.post.id)

    def test_get_post_list_with_title_search(self) -> None:
        url = reverse("post-list")
        response = self.client.get(
            url,
            {
                "search": "테스트 게시글",
                "search_filter": "title",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.post.id)

    def test_get_post_list_with_content_search(self) -> None:
        url = reverse("post-list")
        response = self.client.get(
            url,
            {
                "search": "다른 게시글 본문",
                "search_filter": "content",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.other_post.id)

    def test_get_post_list_with_title_or_content_search(self) -> None:
        url = reverse("post-list")
        response = self.client.get(
            url,
            {
                "search": "자유게시판 글",
                "search_filter": "title_or_content",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.other_post.id)

    def test_get_post_list_with_search_no_result(self) -> None:
        url = reverse("post-list")
        response = self.client.get(
            url,
            {
                "search": "없는검색어",
                "search_filter": "title",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])

    def test_get_post_list_sort_oldest(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url, {"sort": "oldest"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        self.assertEqual(results[0]["id"], self.post.id)
        self.assertEqual(results[1]["id"], self.other_post.id)

    def test_get_post_list_sort_most_views(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url, {"sort": "most_views"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        self.assertEqual(results[0]["id"], self.other_post.id)

    def test_get_post_list_sort_most_likes(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url, {"sort": "most_likes"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        self.assertEqual(len(results), 2)

    def test_get_post_list_sort_most_comments(self) -> None:
        url = reverse("post-list")
        response = self.client.get(url, {"sort": "most_comments"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        self.assertEqual(results[0]["id"], self.post.id)
