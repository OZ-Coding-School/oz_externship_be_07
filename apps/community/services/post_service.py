from typing import Any, cast

from django.db.models import Count, OuterRef, Q, QuerySet, Subquery

from apps.community.models.post_model import Post, PostImage


def get_post_list_queryset(
    search: str,
    search_filter: str,
    category_id: int | None,
    sort: str,
) -> QuerySet[Post]:
    thumbnail_subquery = PostImage.objects.filter(post_id=OuterRef("pk")).order_by("id").values("img_url")[:1]
    queryset: QuerySet[Post] = (
        Post.objects.select_related("author", "category")
        .filter(is_visible=True, category__status=True)
        .annotate(
            like_count=Count("likes", filter=Q(likes__is_liked=True), distinct=True),
            comment_count=Count("postcomment", distinct=True),
            thumbnail_img_url=Subquery(thumbnail_subquery),
        )
    )

    if category_id is not None:
        queryset = queryset.filter(category_id=category_id)

    if search:
        filters = {
            "author": Q(author__nickname__icontains=search),
            "title": Q(title__icontains=search),
            "content": Q(content__icontains=search),
        }
        queryset = queryset.filter(
            filters.get(search_filter, Q(title__icontains=search) | Q(content__icontains=search))
        )

    queryset_any = cast(Any, queryset)
    order_by_map = {
        "oldest": ("created_at", "id"),
        "most_views": ("-view_count", "-id"),
        "most_likes": ("-like_count", "-id"),
        "most_comments": ("-comment_count", "-id"),
    }
    return cast(QuerySet[Post], queryset_any.order_by(*order_by_map.get(sort, ("-created_at", "-id"))))


def get_post_list_values(queryset: QuerySet[Post]) -> Any:
    return cast(Any, queryset).values(
        "id",
        "title",
        "content",
        "view_count",
        "created_at",
        "updated_at",
        "author_id",
        "author__nickname",
        "author__profile_img_url",
        "category__name",
        "like_count",
        "comment_count",
        "thumbnail_img_url",
    )


def build_post_list_response(page_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": post["id"],
            "author": {
                "id": post["author_id"],
                "nickname": post["author__nickname"],
                "profile_img_url": post["author__profile_img_url"],
            },
            "title": post["title"],
            "thumbnail_img_url": post["thumbnail_img_url"],
            "content_preview": f"{post['content'][:50]}..." if len(post["content"]) > 50 else post["content"],
            "comment_count": post["comment_count"],
            "view_count": post["view_count"],
            "like_count": post["like_count"],
            "created_at": post["created_at"],
            "updated_at": post["updated_at"],
            "category_name": post["category__name"],
        }
        for post in page_items
    ]


def get_post_detail(post_id: int) -> Post | None:
    return (
        Post.objects.select_related("author", "category")
        .filter(id=post_id, is_visible=True, category__status=True)
        .annotate(like_count=Count("likes", filter=Q(likes__is_liked=True), distinct=True))
        .first()
    )


def build_post_detail_response(post: Any) -> dict[str, Any]:
    return {
        "id": post.id,
        "title": post.title,
        "author": {
            "id": post.author.id,
            "nickname": post.author.nickname,
            "profile_img_url": post.author.profile_img_url,
        },
        "category": {"id": post.category.id, "name": post.category.name},
        "content": post.content,
        "view_count": post.view_count,
        "like_count": post.like_count,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }
