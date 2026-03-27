from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from django.db.models import Count, F, Q
from django.utils import timezone

from apps.community.core.constants import INSIGHT_RATE_SCALE, INSIGHT_WINDOW_DAYS
from apps.community.models.category_model import PostCategory
from apps.community.models.comment_model import PostComment
from apps.community.models.post_model import Post, PostLike
from apps.users.choices import UserStatus
from apps.users.models.models import User


def _pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * INSIGHT_RATE_SCALE, 2)


def _avg(total: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(total / denominator, 2)


def _activity_user_ids(start: datetime, end: datetime) -> set[int]:
    post_user_ids = set(
        Post.objects.filter(
            is_visible=True,
            category__status=True,
            created_at__gte=start,
            created_at__lt=end,
        ).values_list("author_id", flat=True)
    )
    comment_user_ids = set(
        PostComment.objects.filter(
            post__is_visible=True,
            post__category__status=True,
            created_at__gte=start,
            created_at__lt=end,
        ).values_list("author_id", flat=True)
    )
    like_user_ids = set(
        PostLike.objects.filter(
            is_liked=True,
            post__is_visible=True,
            post__category__status=True,
            updated_at__gte=start,
            updated_at__lt=end,
        ).values_list("user_id", flat=True)
    )
    return post_user_ids | comment_user_ids | like_user_ids


def compute_metrics(snapshot_at: datetime | None = None) -> dict[str, Any]:
    now = snapshot_at or timezone.now()
    since = now - timedelta(days=INSIGHT_WINDOW_DAYS)
    cutoff_24h = now - timedelta(hours=24)

    # 7일 내 공개 게시글(사용자에게 보이는 게시글만)
    window_posts = Post.objects.filter(
        is_visible=True,
        category__status=True,
        created_at__gte=since,
        created_at__lt=now,
    )
    posts_7d_visible_count = window_posts.count()

    # 게시글당 평균 댓글/좋아요
    comments_7d_on_visible_posts_count = PostComment.objects.filter(
        post__in=window_posts,
        created_at__gte=since,
        created_at__lt=now,
    ).count()

    current_active_likes_on_7d_posts_count = PostLike.objects.filter(
        post__in=window_posts,
        is_liked=True,
    ).count()  # 7일 내 게시글에 대한 "현재 활성 좋아요 상태" 스냅샷(좋아요 이벤트 수 아님)

    # 24시간 응답률(분모: 작성 후 24h가 지난 게시글)
    eligible_posts = window_posts.filter(created_at__lt=cutoff_24h)
    eligible_posts_24h_count = eligible_posts.count()

    responded_posts_24h_count = (
        PostComment.objects.filter(
            post__in=eligible_posts,
            created_at__gte=F("post__created_at"),
            created_at__lte=F("post__created_at") + timedelta(hours=24),
        )
        .values("post_id")
        .distinct()
        .count()
    )

    # 카테고리별 게시글 수(활성 카테고리만)
    category_rows = list(
        PostCategory.objects.filter(status=True)
        .annotate(
            post_count=Count(
                "posts",
                filter=Q(
                    posts__is_visible=True,
                    posts__created_at__gte=since,
                    posts__created_at__lt=now,
                ),
            )
        )
        .values_list("name", "post_count")
    )
    category_rows = [(name, int(count)) for name, count in category_rows if int(count) > 0]
    category_rows.sort(key=lambda item: (-item[1], item[0]))
    active_category_post_counts = {name: count for name, count in category_rows}

    category_post_total = sum(active_category_post_counts.values())
    top_category_count = max(active_category_post_counts.values(), default=0)

    # 유저 활성화/정착
    lms_active_users_count = User.objects.filter(
        is_active=True,
        status=UserStatus.ACTIVATED,
    ).count()

    activity_user_ids = _activity_user_ids(since, now)
    community_active_users_count_7d = len(activity_user_ids)

    new_user_ids = set(
        User.objects.filter(
            created_at__gte=since,
            created_at__lt=now,
        ).values_list("id", flat=True)
    )
    new_users_count = len(new_user_ids)
    active_new_users_count_7d = len(activity_user_ids & new_user_ids)

    metrics = {
        "user_activation_rate": _pct(community_active_users_count_7d, lms_active_users_count),
        "new_user_settlement_rate": _pct(active_new_users_count_7d, new_users_count),
        "new_users_count": new_users_count,
        "avg_comments_per_post": _avg(comments_7d_on_visible_posts_count, posts_7d_visible_count),
        "avg_likes_per_post": _avg(current_active_likes_on_7d_posts_count, posts_7d_visible_count),
        "response_rate_within_24h": _pct(responded_posts_24h_count, eligible_posts_24h_count),
        "active_category_post_counts": active_category_post_counts,
        "top1_category_share": _pct(top_category_count, category_post_total),
    }

    raw = {
        "lms_active_users_count": lms_active_users_count,
        "community_active_users_count_7d": community_active_users_count_7d,
        "active_new_users_count_7d": active_new_users_count_7d,
        "posts_7d_visible_count": posts_7d_visible_count,
        "comments_7d_on_visible_posts_count": comments_7d_on_visible_posts_count,
        "current_active_likes_on_7d_posts_count": current_active_likes_on_7d_posts_count,
        "eligible_posts_24h_count": eligible_posts_24h_count,
        "responded_posts_24h_count": responded_posts_24h_count,
        "category_post_total": category_post_total,
    }

    return {
        "snapshot_at": now,
        "window_start": since,
        "window_end": now,
        "metrics": metrics,
        "raw": raw,
    }
