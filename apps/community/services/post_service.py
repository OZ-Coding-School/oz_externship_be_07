
import re
from typing import Any, cast
from django.db.models import Count, OuterRef, Q, QuerySet, Subquery
from martor.utils import markdownify  # type: ignore

from apps.community.models.post_model import Post, PostAttachment, PostImage


def get_post_list_queryset(
    search: str,
    search_filter: str,
    category_id: int | None,
    sort: str,
) -> QuerySet[Post]:
    queryset: QuerySet[Post] = (
        Post.objects.select_related("author", "category")
        .filter(is_visible=True, category__status=True)
        .annotate(
            like_count=Count("likes", filter=Q(likes__is_liked=True), distinct=True),
            comment_count=Count("postcomment", distinct=True),
            thumbnail_img_url=Subquery(
                PostImage.objects.filter(post_id=OuterRef("pk")).order_by("id").values("img_url")[:1]
            ),
        )
    )
    if category_id is not None:
        queryset = queryset.filter(category_id=category_id)
    if search:
        queryset = queryset.filter(
            {
                "author": Q(author__nickname__icontains=search),
                "title": Q(title__icontains=search),
                "content": Q(content__icontains=search),
            }.get(search_filter, Q(title__icontains=search) | Q(content__icontains=search))
        )
    return cast(
        QuerySet[Post],
        cast(Any, queryset).order_by(
            *{
                "oldest": ("created_at", "id"),
                "most_views": ("-view_count", "-id"),
                "most_likes": ("-like_count", "-id"),
                "most_comments": ("-comment_count", "-id"),
            }.get(sort, ("-created_at", "-id"))
        ),
    )


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
        "content": markdownify(post.content),
        "view_count": post.view_count,
        "like_count": post.like_count,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }

def create_post(author: Any, title: str, content: str, category: int) -> Post:
    return Post.objects.create(
        author=author,
        title=title,
        content=content,
        category=category,
    )

def update_post(instance: Post, title: str, content: str, category: int) -> None:
    instance.title = title
    instance.content = content
    instance.category = category

    instance.save()

def delete_post(instance: Post) -> None:
    instance.delete()

def post_file_delete(instance: Post) -> None:
    if not instance:
        attachments = PostAttachment.objects.filter(post=instance)

        attachments.delete()

def post_image_delete(instance: Post) -> None:
    if not instance:
        images = PostImage.objects.filter(post=instance)

        images.delete()

def post_file_save(instance: Post) -> None:
    image_url = re.findall(r'(!?)\[(.*?)\]\((https?://[^\s\)]+)', instance.content)
    for is_image, name, url in image_url:
        if  is_image:
            PostImage.objects.create(post=instance, img_url=url)
        else:
            PostAttachment.objects.create(post=instance, file_name=name, file_url=url)

def file_synchronization(instance: Post) -> None:
    current_image_urls = re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', instance.content)
    image_delete = PostImage.objects.filter(post=instance).exclude(img_url__in=current_image_urls)

    PostImage.objects.filter(post=instance).exclude(img_url__in=current_image_urls).delete()

    existing_db_urls = PostImage.objects.filter(post=instance).values_list("img_url", flat=True)
    for url in current_image_urls:
        if url not in existing_db_urls:
            PostImage.objects.create(post=instance, img_url=url)

    current_attachments = re.findall(r'(?<!\!)\[(.*?)\]\((https?://[^\)]+)\)', instance.content)
    current_att_urls = [url for name, url in current_attachments]

    file_delete = PostAttachment.objects.filter(post=instance).exclude(file_url__in=current_att_urls)

    PostAttachment.objects.filter(post=instance).exclude(file_url__in=current_att_urls).delete()

    existing_att_urls = PostAttachment.objects.filter(post=instance).values_list("file_url", flat=True)
    for name, url in current_attachments:
        if url not in existing_att_urls:
            PostAttachment.objects.create(post=instance, file_name=name, file_url=url)