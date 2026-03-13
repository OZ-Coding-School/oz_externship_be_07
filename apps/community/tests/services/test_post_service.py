from django.test import TestCase

from apps.community.models.category_model import PostCategory
from apps.community.models.comment_model import PostComment
from apps.community.models.post_model import Post, PostImage, PostLike
from apps.community.services.post_service import (
    build_post_detail_response,
    build_post_list_response,
    get_post_detail,
    get_post_list_queryset,
    get_post_list_values,
)
from apps.users.models.models import User


class PostServiceTest(TestCase):
    user: User
    other_user: User
    category: PostCategory
    other_category: PostCategory
    post: Post
    other_post: Post

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            email="test@test.com",
            name="testuser",
            password="password123",
            birthday="2000-01-01",
        )

        cls.other_user = User.objects.create(
            email="other@test.com",
            name="otheruser",
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

    def test_get_post_list_queryset_with_category_filter(self) -> None:
        queryset = get_post_list_queryset(
            search="",
            search_filter="",
            category_id=self.category.id,
            sort="latest",
        )

        self.assertEqual(queryset.count(), 1)

        first_post = queryset.first()
        self.assertIsNotNone(first_post)
        assert first_post is not None
        self.assertEqual(first_post.id, self.post.id)

    def test_get_post_list_queryset_with_author_search(self) -> None:
        queryset = get_post_list_queryset(
            search=self.user.nickname,
            search_filter="author",
            category_id=None,
            sort="latest",
        )

        self.assertEqual(queryset.count(), 1)

        first_post = queryset.first()
        self.assertIsNotNone(first_post)
        assert first_post is not None
        self.assertEqual(first_post.id, self.post.id)

    def test_get_post_list_queryset_with_title_search(self) -> None:
        queryset = get_post_list_queryset(
            search="테스트 게시글",
            search_filter="title",
            category_id=None,
            sort="latest",
        )

        self.assertEqual(queryset.count(), 1)

        first_post = queryset.first()
        self.assertIsNotNone(first_post)
        assert first_post is not None
        self.assertEqual(first_post.id, self.post.id)

    def test_get_post_list_queryset_with_content_search(self) -> None:
        queryset = get_post_list_queryset(
            search="다른 게시글 본문",
            search_filter="content",
            category_id=None,
            sort="latest",
        )

        self.assertEqual(queryset.count(), 1)

        first_post = queryset.first()
        self.assertIsNotNone(first_post)
        assert first_post is not None
        self.assertEqual(first_post.id, self.other_post.id)

    def test_get_post_list_queryset_with_title_or_content_search(self) -> None:
        queryset = get_post_list_queryset(
            search="자유게시판 글",
            search_filter="title_or_content",
            category_id=None,
            sort="latest",
        )

        self.assertEqual(queryset.count(), 1)

        first_post = queryset.first()
        self.assertIsNotNone(first_post)
        assert first_post is not None
        self.assertEqual(first_post.id, self.other_post.id)

    def test_get_post_list_queryset_sort_oldest(self) -> None:
        queryset = get_post_list_queryset(
            search="",
            search_filter="",
            category_id=None,
            sort="oldest",
        )

        posts = list(queryset)
        self.assertEqual(posts[0].id, self.post.id)
        self.assertEqual(posts[1].id, self.other_post.id)

    def test_get_post_list_queryset_sort_most_views(self) -> None:
        queryset = get_post_list_queryset(
            search="",
            search_filter="",
            category_id=None,
            sort="most_views",
        )

        posts = list(queryset)
        self.assertEqual(posts[0].id, self.other_post.id)

    def test_get_post_list_queryset_sort_most_likes(self) -> None:
        queryset = get_post_list_queryset(
            search="",
            search_filter="",
            category_id=None,
            sort="most_likes",
        )

        posts = list(queryset)
        self.assertEqual(len(posts), 2)

    def test_get_post_list_queryset_sort_most_comments(self) -> None:
        queryset = get_post_list_queryset(
            search="",
            search_filter="",
            category_id=None,
            sort="most_comments",
        )

        posts = list(queryset)
        self.assertEqual(posts[0].id, self.post.id)

    def test_get_post_list_values_returns_expected_fields(self) -> None:
        queryset = get_post_list_queryset(
            search="",
            search_filter="",
            category_id=None,
            sort="latest",
        )

        values = list(get_post_list_values(queryset))
        first_item = values[0]

        self.assertIn("id", first_item)
        self.assertIn("title", first_item)
        self.assertIn("content", first_item)
        self.assertIn("author_id", first_item)
        self.assertIn("author__nickname", first_item)
        self.assertIn("author__profile_img_url", first_item)
        self.assertIn("category__name", first_item)
        self.assertIn("like_count", first_item)
        self.assertIn("comment_count", first_item)
        self.assertIn("thumbnail_img_url", first_item)

    def test_build_post_list_response_returns_expected_data(self) -> None:
        page_items = [
            {
                "id": self.post.id,
                "author_id": self.user.id,
                "author__nickname": self.user.nickname,
                "author__profile_img_url": self.user.profile_img_url,
                "title": self.post.title,
                "content": self.post.content,
                "thumbnail_img_url": "https://example.com/image1.png",
                "comment_count": 1,
                "view_count": self.post.view_count,
                "like_count": 1,
                "created_at": self.post.created_at,
                "updated_at": self.post.updated_at,
                "category__name": self.category.name,
            }
        ]

        result = build_post_list_response(page_items)

        self.assertEqual(result[0]["id"], self.post.id)
        self.assertEqual(result[0]["author"]["id"], self.user.id)
        self.assertEqual(result[0]["category_name"], self.category.name)
        self.assertEqual(result[0]["thumbnail_img_url"], "https://example.com/image1.png")

    def test_get_post_detail_success(self) -> None:
        post = get_post_detail(self.post.id)

        self.assertIsNotNone(post)
        assert post is not None
        self.assertEqual(post.id, self.post.id)

    def test_get_post_detail_not_found(self) -> None:
        post = get_post_detail(999999)

        self.assertIsNone(post)

    def test_build_post_detail_response_returns_expected_data(self) -> None:
        post = get_post_detail(self.post.id)

        self.assertIsNotNone(post)
        assert post is not None

        response = build_post_detail_response(post)

        self.assertEqual(response["id"], self.post.id)
        self.assertEqual(response["title"], self.post.title)
        self.assertEqual(response["content"], self.post.content)
        self.assertEqual(response["author"]["id"], self.user.id)
        self.assertEqual(response["category"]["id"], self.category.id)
        self.assertIn("view_count", response)
        self.assertIn("like_count", response)
        self.assertIn("created_at", response)
        self.assertIn("updated_at", response)
