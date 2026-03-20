from datetime import date
from typing import Any

from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.test import TestCase
from django.urls import reverse

from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post
from apps.users.models.models import User


class PostCategoryAdminTest(TestCase):
    admin_user: User
    author: User
    active_category: PostCategory
    inactive_with_posts: PostCategory
    inactive_no_posts: PostCategory
    post_in_inactive: Post

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="testyo!",
            name="관리자",
            nickname="admin01",
            phone_number="01011112222",
            gender="M",
            birthday=date(1990, 1, 1),
        )
        cls.author = User.objects.create_user(
            email="user@test.com",
            password="testyo!",
            name="작성자",
            nickname="testuser01",
            phone_number="01033334444",
            gender="M",
            birthday=date(2000, 1, 1),
        )

        cls.active_category = PostCategory.objects.create(name="활성 카테고리", status=True)
        cls.inactive_with_posts = PostCategory.objects.create(name="비활성-게시글있음", status=False)
        cls.inactive_no_posts = PostCategory.objects.create(name="비활성-게시글없음", status=False)

        cls.post_in_inactive = Post.objects.create(
            title="삭제 미리보기 게시글",
            content="테스트 본문",
            author=cls.author,
            category=cls.inactive_with_posts,
            is_visible=True,
        )

    def setUp(self) -> None:
        self.client.force_login(self.admin_user)

    def _bulk_delete(self, category_ids: list[int]) -> Any:
        url = reverse("admin:community_postcategory_changelist")
        return self.client.post(
            url,
            {
                "action": "delete_category_by_policy",
                "index": "0",
                ACTION_CHECKBOX_NAME: [str(pk) for pk in category_ids],
            },
            follow=True,
        )

    def test_delete_view_blocks_active_category(self) -> None:
        url = reverse("admin:community_postcategory_delete", args=[self.active_category.pk])

        response = self.client.post(url, {"post": "yes"}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(PostCategory.objects.filter(pk=self.active_category.pk).exists())
        self.assertContains(response, "활성 카테고리")
        self.assertContains(response, "삭제할 수 없습니다")

    def test_delete_confirm_page_shows_related_post_preview_for_inactive_category(self) -> None:
        url = reverse("admin:community_postcategory_delete", args=[self.inactive_with_posts.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "연결된 게시글 1건도 함께 삭제")
        self.assertContains(response, "연결 게시글 1건")
        self.assertContains(response, self.post_in_inactive.title)

    def test_bulk_delete_requires_second_confirmation_and_deletes_only_inactive(self) -> None:
        first = self._bulk_delete([self.active_category.pk, self.inactive_with_posts.pk])

        self.assertEqual(first.status_code, 200)
        self.assertContains(first, "활성 카테고리는 삭제할 수 없습니다")
        self.assertContains(first, "삭제 확인:")
        self.assertTrue(PostCategory.objects.filter(pk=self.active_category.pk).exists())
        self.assertTrue(PostCategory.objects.filter(pk=self.inactive_with_posts.pk).exists())

        second = self._bulk_delete([self.active_category.pk, self.inactive_with_posts.pk])

        self.assertEqual(second.status_code, 200)
        self.assertContains(second, "삭제 완료: 카테고리 1개, 게시글 1개")
        self.assertTrue(PostCategory.objects.filter(pk=self.active_category.pk).exists())
        self.assertFalse(PostCategory.objects.filter(pk=self.inactive_with_posts.pk).exists())
        self.assertFalse(Post.objects.filter(pk=self.post_in_inactive.pk).exists())

    def test_bulk_delete_inactive_without_posts(self) -> None:
        self._bulk_delete([self.inactive_no_posts.pk])
        second = self._bulk_delete([self.inactive_no_posts.pk])

        self.assertEqual(second.status_code, 200)
        self.assertContains(second, "삭제 완료: 카테고리 1개, 게시글 0개")
        self.assertFalse(PostCategory.objects.filter(pk=self.inactive_no_posts.pk).exists())
