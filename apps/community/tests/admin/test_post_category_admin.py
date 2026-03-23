import hashlib
import time
from datetime import date
from typing import Any

from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.test import TestCase
from django.urls import reverse

from apps.community.admin import PostCategoryAdmin
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

    def _bulk_confirm_session_key(self, category_ids: list[int]) -> str:
        token_raw = ",".join(str(pk) for pk in sorted(category_ids))
        token = hashlib.sha256(token_raw.encode("utf-8")).hexdigest()[: PostCategoryAdmin.DELETE_CONFIRM_TOKEN_LENGTH]
        prefix = PostCategoryAdmin.DELETE_CONFIRM_SESSION_KEY_PREFIX
        return f"{prefix}:bulk:{token}"

    def test_delete_view_blocks_active_category(self) -> None:
        """활성 카테고리 상세 차단 확인"""
        url = reverse("admin:community_postcategory_delete", args=[self.active_category.pk])

        response = self.client.post(url, {"post": "yes"}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(PostCategory.objects.filter(pk=self.active_category.pk).exists())
        self.assertContains(response, "활성 카테고리")
        self.assertContains(response, "삭제할 수 없습니다")

    def test_formfield_for_foreignkey_excludes_inactive_on_add_and_keeps_current_on_change(self) -> None:
        """게시글 생성/수정 화면 카테고리 드롭다운 노출 확인"""
        add_url = reverse("admin:community_post_add")
        add_response = self.client.get(add_url)
        self.assertEqual(add_response.status_code, 200)

        add_qs = add_response.context["adminform"].form.fields["category"].queryset
        self.assertIn(self.active_category, add_qs)
        self.assertNotIn(self.inactive_with_posts, add_qs)

        change_url = reverse("admin:community_post_change", args=[self.post_in_inactive.pk])
        change_response = self.client.get(change_url)
        self.assertEqual(change_response.status_code, 200)

        change_qs = change_response.context["adminform"].form.fields["category"].queryset
        self.assertIn(self.active_category, change_qs)
        self.assertIn(self.inactive_with_posts, change_qs)

    def test_save_model_warns_on_deactivation_with_visible_posts(self) -> None:
        """활성 -> 비활성 전환 시, 경고 메시지(해당 공개 게시글) 출력 확인"""
        Post.objects.create(
            title="활성 카테고리 공개글",
            content="본문",
            author=self.author,
            category=self.active_category,
            is_visible=True,
        )

        url = reverse("admin:community_postcategory_change", args=[self.active_category.pk])
        response = self.client.post(
            url,
            {
                "name": self.active_category.name,
                "_save": "저장",  # status 미전송 -> False
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.active_category.refresh_from_db()
        self.assertFalse(self.active_category.status)
        self.assertContains(response, "카테고리를 비활성화했습니다")
        self.assertContains(response, "공개 상태 게시글 1건")

    def test_delete_confirm_page_shows_related_post_preview_for_inactive_category(self) -> None:
        """비활성 카테고리 상세 삭제 화면, 게시글 미리보기 확인"""
        url = reverse("admin:community_postcategory_delete", args=[self.inactive_with_posts.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "연결된 게시글 1건도 함께 삭제")
        self.assertContains(response, "연결 게시글 1건")
        self.assertContains(response, self.post_in_inactive.title)

    def test_detail_delete_inactive_with_posts(self) -> None:
        """비활성 카테고리 상세 삭제 시 게시글 연쇄 삭제 확인"""
        url = reverse("admin:community_postcategory_delete", args=[self.inactive_with_posts.pk])

        response = self.client.post(url, {"post": "yes"}, follow=True)  # "post": "yes" -> 확인 후, 최종 삭제 요청

        self.assertEqual(response.status_code, 200)
        self.assertFalse(PostCategory.objects.filter(pk=self.inactive_with_posts.pk).exists())
        self.assertFalse(Post.objects.filter(pk=self.post_in_inactive.pk).exists())

    def test_bulk_delete_requires_second_confirmation_and_deletes_only_inactive(self) -> None:
        """목록 삭제 2회 실행 시 비활성 카테고리만 삭제되는지 확인"""
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

    def test_bulk_delete_ttl_expired_requires_first_step_again(self) -> None:
        """TTL 만료 후 목록 삭제 재확인 단계 초기화 확인"""
        target_ids = [self.inactive_no_posts.pk]

        first_step = self._bulk_delete(target_ids)
        self.assertEqual(first_step.status_code, 200)
        self.assertContains(first_step, "삭제 확인:")

        session_key = self._bulk_confirm_session_key(target_ids)
        session = self.client.session
        self.assertIn(session_key, session)

        payload = session[session_key]
        payload["ts"] = int(time.time()) - (PostCategoryAdmin.DELETE_CONFIRM_TTL_SECONDS + 1)  # TTL(60초) 만료
        session[session_key] = payload
        session.save()

        second_step = self._bulk_delete(target_ids)
        self.assertEqual(second_step.status_code, 200)
        self.assertContains(second_step, "삭제 확인:")  # 다시 1단계
        self.assertTrue(PostCategory.objects.filter(pk=self.inactive_no_posts.pk).exists())

    def test_bulk_delete_inactive_without_posts(self) -> None:
        """게시글 없는 비활성 카테고리 목록 삭제 확인"""
        self._bulk_delete([self.inactive_no_posts.pk])
        second = self._bulk_delete([self.inactive_no_posts.pk])

        self.assertEqual(second.status_code, 200)
        self.assertContains(second, "삭제 완료: 카테고리 1개, 게시글 0개")
        self.assertFalse(PostCategory.objects.filter(pk=self.inactive_no_posts.pk).exists())
