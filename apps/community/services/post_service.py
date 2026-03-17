import os
import uuid
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


def create_post_image(post: Post, image_url: str) -> PostImage:
    return PostImage.objects.create(post=post, img_url=image_url)


def create_post_attachment(post: Post, file_url: str, file_name: str) -> PostAttachment:
    return PostAttachment.objects.create(post=post, file_url=file_url, file_name=file_name)


def update_post(instance: Post, validated_data: dict[str, Any]) -> Post:
    for key, value in validated_data.items():
        setattr(instance, key, value)

    instance.save()
    return instance


def delete_post(instance: Post) -> None:
    instance.delete()


def post_file_upload(instance: Post, file: UploadedFile) -> None:
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
    if not file or not file.name:
        return
    name, file_extension = os.path.splitext(file.name)
    file_extension = file_extension.lower()

    ex_file_name = f"{uuid.uuid4()}{file_extension}"
    if file_extension in image_extensions:
        file_path = default_storage.save(f"post_images/{ex_file_name}", file)
        file_url = default_storage.url(file_path)

        if file_url not in instance.content:
            create_post_image(instance, file_url)

            instance.content += f"\n\n![이미지]({file_url})"
            instance.save()
    else:
        file_path = default_storage.save(f"post_attachments/{ex_file_name}", file)
        file_url = default_storage.url(file_path)

        create_post_attachment(instance, file_url, file.name)
