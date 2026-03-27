from datetime import date, datetime, timedelta
from typing import Any

from django.test import TestCase
from django.utils import timezone

from apps.community.insights.metrics import compute_metrics
from apps.community.models.category_model import PostCategory
from apps.community.models.comment_model import PostComment
from apps.community.models.post_model import Post, PostLike
from apps.users.choices import UserStatus
from apps.users.models.models import User


class CommunityInsightMetricsTest(TestCase):
    def _dt(self, y: int, m: int, d: int, h: int = 0, minute: int = 0, sec: int = 0) -> datetime:
        return timezone.make_aware(datetime(y, m, d, h, minute, sec), timezone.get_current_timezone())

    def _set_ts(self, obj: Any, ts: datetime) -> None:
        model = obj.__class__
        model.objects.filter(pk=obj.pk).update(created_at=ts, updated_at=ts)
        obj.refresh_from_db()

    def _create_user(
        self,
        idx: int,
        *,
        status: str = UserStatus.ACTIVATED,
        is_active: bool = True,
    ) -> User:
        user = User.objects.create(
            email=f"user{idx}@example.com",
            name=f"user{idx}",
            nickname=f"nick{idx}",
            phone_number=f"010{idx:08d}",
            gender="M",
            birthday=date(2000, 1, 1),
            status=status,
            is_active=is_active,
            password="pw",
        )
        return user

    def _assert_metric(self, metrics: dict[str, object], key: str, expected: float | dict[str, int]) -> None:
        self.assertEqual(metrics[key], expected)

    def test_compute_metrics_definition_lock_and_delta(self) -> None:
        """정의규칙(분모/경계/카테고리 분모)과 델타 키 노출을 함께 검증"""
        now = self._dt(2026, 4, 1, 12, 0, 0)
        current_start = now - timedelta(days=7)
        previous_start = current_start - timedelta(days=7)

        # users
        u1 = self._create_user(1)
        u2 = self._create_user(2)
        u3 = self._create_user(3)
        u4 = self._create_user(4)  # 비참여 활성 유저(분모 포함 확인용)
        nu1 = self._create_user(5)
        nu2 = self._create_user(6, status=UserStatus.DEACTIVATED, is_active=False)  # 신규 분모 포함 확인용

        self._set_ts(u1, self._dt(2026, 3, 10, 9))
        self._set_ts(u2, self._dt(2026, 3, 10, 9))
        self._set_ts(u3, self._dt(2026, 3, 10, 9))
        self._set_ts(u4, self._dt(2026, 3, 10, 9))
        self._set_ts(nu1, current_start + timedelta(hours=1))
        self._set_ts(nu2, current_start + timedelta(hours=2))

        cat_a = PostCategory.objects.create(name="A", status=True)
        cat_b = PostCategory.objects.create(name="B", status=True)
        cat_inactive = PostCategory.objects.create(name="X", status=False)

        # current window posts
        p1 = Post.objects.create(title="p1", content="c", author=u1, category=cat_a, is_visible=True)
        p2 = Post.objects.create(title="p2", content="c", author=u1, category=cat_a, is_visible=True)
        p3 = Post.objects.create(title="p3", content="c", author=u1, category=cat_b, is_visible=True)
        p_hidden_cat = Post.objects.create(title="p4", content="c", author=u1, category=cat_inactive, is_visible=True)

        self._set_ts(p1, current_start + timedelta(days=1))
        self._set_ts(p2, current_start + timedelta(days=2))
        self._set_ts(p3, current_start + timedelta(days=3))
        self._set_ts(p_hidden_cat, current_start + timedelta(days=3))

        # previous window post (delta용)
        p_prev = Post.objects.create(title="prev", content="c", author=u1, category=cat_b, is_visible=True)
        self._set_ts(p_prev, previous_start + timedelta(days=1))

        # 댓글 (response 24h 경계 포함/제외)
        c1 = PostComment.objects.create(post=p1, author=u2, content="in-24h")
        c2 = PostComment.objects.create(post=p2, author=nu1, content="out-24h")
        c_prev = PostComment.objects.create(post=p_prev, author=u2, content="prev")

        self._set_ts(c1, p1.created_at + timedelta(hours=24))  # 포함
        self._set_ts(c2, p2.created_at + timedelta(hours=24, seconds=1))  # 제외
        self._set_ts(c_prev, p_prev.created_at + timedelta(hours=2))

        # 좋아요
        l1 = PostLike.objects.create(post=p1, user=u3, is_liked=True)
        l2 = PostLike.objects.create(post=p2, user=u2, is_liked=True)
        l3 = PostLike.objects.create(post=p3, user=u1, is_liked=False)
        l_prev = PostLike.objects.create(post=p_prev, user=u3, is_liked=True)

        self._set_ts(l1, current_start + timedelta(days=4))
        self._set_ts(l2, current_start + timedelta(days=5))
        self._set_ts(l3, current_start + timedelta(days=5))
        self._set_ts(l_prev, previous_start + timedelta(days=2))

        result = compute_metrics(snapshot_at=now)
        metrics = result["current"]["metrics"]
        raw = result["current"]["raw"]
        deltas = result["deltas"]

        # 1) activation 분모는 LMS 전체 활성 유저(비참여 u4 포함, 비활성 nu2 제외)
        self.assertEqual(raw["lms_active_users_count"], 5)
        self.assertEqual(raw["community_active_users_count_7d"], 4)
        self._assert_metric(metrics, "user_activation_rate", 80.0)  # 4/5*100

        # 2) response 24h 조건: =24h 포함, +1초 제외
        self.assertEqual(raw["eligible_posts_24h_count"], 3)
        self.assertEqual(raw["responded_posts_24h_count"], 1)
        self._assert_metric(metrics, "response_rate_within_24h", 33.33)

        # 3) top1 분모는 active category post count 합계(2+1)
        self._assert_metric(metrics, "active_category_post_counts", {"A": 2, "B": 1})
        self._assert_metric(metrics, "top1_category_share", 66.67)

        # 기본 집계
        self.assertEqual(metrics["new_users_count"], 2)
        self._assert_metric(metrics, "new_user_settlement_rate", 50.0)
        self._assert_metric(metrics, "avg_comments_per_post", 0.67)
        self._assert_metric(metrics, "avg_likes_per_post", 0.67)

        # delta 존재(활성화율 해석 보조 raw delta 포함)
        self.assertIn("community_active_users_count_7d_delta", deltas)
        self.assertIn("lms_active_users_count_delta", deltas)

    def test_compute_metrics_zero_denominator_guard(self) -> None:
        """분모 0 상황에서 비율/평균 지표가 0으로 안전 처리되는지 검증"""
        now = self._dt(2026, 4, 1, 12, 0, 0)
        result = compute_metrics(snapshot_at=now)
        metrics = result["current"]["metrics"]

        self._assert_metric(metrics, "avg_comments_per_post", 0.0)
        self._assert_metric(metrics, "avg_likes_per_post", 0.0)
        self._assert_metric(metrics, "response_rate_within_24h", 0.0)
        self._assert_metric(metrics, "new_user_settlement_rate", 0.0)
        self._assert_metric(metrics, "top1_category_share", 0.0)
