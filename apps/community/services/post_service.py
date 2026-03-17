import os
import uuid
from pathlib import Path
from typing import Any, cast

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
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


User = get_user_model()


def create_post(author: Any, validated_data: dict[str, Any]) -> Post:
    return Post.objects.create(author=author, **validated_data)

def update_post(instance: Post, validated_data: dict[str, Any]) -> Post:
    for key, value in validated_data.items():
        setattr(instance, key, value)

    instance.save()
    return instance

def delete_post(instance: Post) -> None:
    instance.delete()

def post_file_delete(instance: Post) -> None:
    attachments = PostAttachment.objects.filter(post=instance)

    for attachment in attachments:
        path = attachment.file_url.split("/post_attachments/")[-1]
        default_storage.delete(path)

    attachments.delete()

def post_image_delete(instance: Post) -> None:
    images = PostImage.objects.filter(post=instance)

    for image in images:
        path = image.img_url.split("/post_images/")[-1]
        default_storage.delete(path)

    images.delete()

def post_file_save(instance: Post, file_name: str, file_url: str) -> PostAttachment:
    return PostAttachment.objects.create(Post=instance, file_name=file_name, file_url=file_url)

def post_image_save(instance: Post, file_url: str) -> PostImage:
    return PostImage.objects.create(Post=instance, file_url=file_url)

def upload_file(file: UploadedFile) -> dict[str, str]:
    original_name = file.name
    extension = Path(file.name).suffix.lower()
    file_name = f"{uuid.uuid4()}{extension}"

    image_extension = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]

    if extension in image_extension:
        folder = "post_images"
        markdown = f"![이미지]({{url}})"
    else:
        folder = "post_attachment"
        markdown = f"[{original_name}]({{url}})"

    file_path = default_storage.save(f"{folder}/{file_name}", file)
    file_url = default_storage.url(file_path)

    return {
        "file_url": file_url,
        "file_name": file_name,
        "markdown": markdown.format(url=file_url)
    }