import json
import logging
import re
from typing import Any, cast

import boto3
import requests
from aiohttp import ClientError
from botocore.config import Config
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Count, OuterRef, Q, QuerySet, Subquery

from apps.community.models.category_model import PostCategory
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


def build_post_detail_response(post: Post) -> dict[str, Any]:
    return {
        "id": post.id,
        "author": {
            "id": post.author.id,
            "nickname": post.author.nickname,
            "profile_img_url": post.author.profile_img_url,
        },
        "category_name": post.category.name,
        "title": post.title,
        "content": post_detail_file_presigned_url(post.content),
        "view_count": post.view_count,
        "like_count": getattr(post, "like_count", 0),
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }


def create_post(author: Any, title: str, content: str, category: PostCategory) -> Post:
    """게시판 생성 함수"""

    return Post.objects.create(
        author=author,
        title=title,
        content=content,
        category=category,
    )


def update_post(instance: Post, title: str, content: str, category: PostCategory) -> None:
    """게시판 수정 함수"""

    instance.title = title
    instance.content = content
    instance.category = category

    instance.save()


def post_file_save(instance: Post) -> None:
    """본문에서 마크다운 이미지/파일 url 추출 저장 함수"""

    image_url = re.findall(r"(!?)\[(.*?)\]\((https?://[^\s\)]+)", instance.content)
    for is_image, name, url in image_url:
        if is_image == "!":
            PostImage.objects.create(post=instance, img_url=url)
        else:
            PostAttachment.objects.create(post=instance, file_name=name, file_url=url)


def file_synchronization(instance: Post) -> None:
    """본문 이미지 제거 및 추가시 삭제 추가 함수"""

    current_image_urls = re.findall(r"!\[.*?\]\((https?://[^?)\s]+)(?:\?.*?)?\)", instance.content)

    existing_db_urls = PostImage.objects.filter(post=instance).values_list("img_url", flat=True)
    for url in current_image_urls:
        if url not in existing_db_urls:
            PostImage.objects.create(post=instance, img_url=url)

    current_attachments = re.findall(r"(?<!\!)\[(.*?)\]\((https?://[^?)\s]+)(?:\?.*?)?\)", instance.content)

    existing_att_urls = PostAttachment.objects.filter(post=instance).values_list("file_url", flat=True)
    for name, url in current_attachments:
        if url not in existing_att_urls:
            PostAttachment.objects.create(post=instance, file_name=name, file_url=url)


def file_delete(url: list[str]) -> None:
    """실제 파일 삭제 함수"""

    for file_url in url:
        key_url = file_url.split("com/")
        if len(key_url) > 1:
            aws_url = s3_url(key_url[1])
            if default_storage.exists(aws_url):
                default_storage.delete(aws_url)


def post_detail_file_presigned_url(content: str) -> str:
    select_file = re.findall(r"(!?)\[(.*?)\]\((https?://[^\s\)]+)\)", content)
    for is_image, name, url in select_file:
        if is_image != "!":
            is_image = ""

        if "?" in url:
            key_url = url.split("?")[0]
            content = content.replace(f"{is_image}[{name}]({key_url})", f"{is_image}[{name}]({url})")
        else:
            key_url = url.split("com/")[1]
            get_url = s3_url(key_url)

            content = content.replace(f"{is_image}[{name}]({url})", f"{is_image}[{name}]({get_url})")

    return content


def s3_url(key_url: str) -> str:
    """AWS S3 Presigned url GET"""
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION,
    )
    try:
        s3_value = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_S3_BUCKET_NAME,
                "Key": key_url,
            },
            ExpiresIn=3600,
        )
    except ClientError as e:
        logger = logging.getLogger(__name__)
        logger.error(e)
        return key_url
    return s3_value
