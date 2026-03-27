import logging
from typing import Any, cast

from botocore.exceptions import ClientError
from django.core.files.storage import default_storage
from django.db.models import CharField, Count, Q, QuerySet, Value

from apps.community.core.constants import (
    RE_ATTACHMENT_URL,
    RE_FILE_URL_STRIP_QS,
    RE_IMAGE_URL,
    RE_MARKDOWN_LINK,
    RIST_SPLIT,
)
from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post, PostAttachment, PostImage
from apps.core.utils.s3_handler import S3Handler


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
            thumbnail_img_url=Value("", output_field=CharField()),
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
                "profile_img_url": s3_url(post["author__profile_img_url"]),
            },
            "title": post["title"],
            "thumbnail_img_url": content_top_img(post["content"]),
            "content_preview": content_img_not_url(post["content"]),
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
        "category_id": post.category.id,
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
    """게시글 수정 함수"""

    instance.title = title
    instance.content = content
    instance.category = category

    instance.save(update_fields=["title", "content", "category", "updated_at"])


def post_delete(instance: Post) -> None:
    instance.delete()


def post_file_save(instance: Post) -> None:
    """본문에서 마크다운 이미지/파일 url 추출 저장 함수"""

    image_url = RE_MARKDOWN_LINK.findall(instance.content)
    for is_image, name, url in image_url:
        if is_image == "!":
            PostImage.objects.create(post=instance, img_url=url)
        else:
            PostAttachment.objects.create(post=instance, file_name=name, file_url=url)


def file_synchronization(instance: Post) -> None:
    """본문 이미지 제거 및 추가시 삭제 추가 함수"""
    post_update_file_presigned_url(instance)

    current_image_urls = RE_IMAGE_URL.findall(instance.content)

    existing_db_urls = PostImage.objects.filter(post=instance).values_list("img_url", flat=True)
    for url in current_image_urls:
        if url not in existing_db_urls:
            PostImage.objects.create(post=instance, img_url=url)

    current_attachments = RE_ATTACHMENT_URL.findall(instance.content)

    existing_att_urls = PostAttachment.objects.filter(post=instance).values_list("file_url", flat=True)
    for name, url in current_attachments:
        if url not in existing_att_urls:
            PostAttachment.objects.create(post=instance, file_name=name, file_url=url)


def post_delete_sum(instance: Post) -> None:
    post_file_delete(instance)
    post_delete(instance)


def post_file_delete(instance: Post) -> None:
    """PostImage DB 데이터 삭제 함수"""

    if instance:
        images = PostImage.objects.filter(post=instance)
        file_delete(set(images.values_list("img_url", flat=True)))
        images.delete()

        file = PostAttachment.objects.filter(post=instance)
        file_delete(set(file.values_list("file_url", flat=True)))
        file.delete()


def file_delete(url: set[str]) -> None:
    """실제 파일 삭제 함수"""

    for file_url in url:
        key_url = file_url.split(RIST_SPLIT)
        try:
            if default_storage.exists(key_url[1]):
                default_storage.delete(key_url[1])
        except IndexError as e:
            logging.getLogger(__name__).error(f"file delete error: {e}")


def post_detail_file_presigned_url(content: str) -> str:
    """Presigned url 주소 변환"""

    select_file = set(RE_MARKDOWN_LINK.findall(content))
    s3_url_change = {}
    for is_image, name, url in select_file:
        if is_image != "!":
            is_image = ""

        if "?" in url:
            key_url = url.split("?")[0]
            original = f"{is_image}[{name}]({url})"
            new = f"{is_image}[{name}]({key_url})"

        else:
            key_url = url.split(RIST_SPLIT)[1]
            get_url = s3_url(key_url)
            original = f"{is_image}[{name}]({url})"
            new = f"{is_image}[{name}]({get_url})"

        s3_url_change[original] = new

    for order_url, new_url in s3_url_change.items():
        content = content.replace(order_url, new_url)

    return content


def post_update_file_presigned_url(instance: Post) -> None:
    old_file_urls = RE_FILE_URL_STRIP_QS.findall(instance.content)
    image_urls = [match[2] for match in old_file_urls if match[0] == "!"]
    file_urls = [match[2] for match in old_file_urls if match[0] == ""]

    delete_image = PostImage.objects.filter(post=instance).exclude(img_url__in=image_urls)
    if delete_image:
        file_delete(set(delete_image.values_list("img_url", flat=True)))
        delete_image.delete()

    delete_file = PostAttachment.objects.filter(post=instance).exclude(file_url__in=file_urls)
    if delete_file:
        file_delete(set(delete_file.values_list("file_url", flat=True)))
        delete_file.delete()


def s3_url(key_url: str) -> str:
    """AWS S3 Presigned url GET"""
    if not key_url:
        return key_url
    try:
        s3_value = S3Handler().generate_get_presigned_url(key_url)
    except ClientError as e:
        logger = logging.getLogger(__name__)
        logger.error(e)
        return key_url
    return s3_value


def content_img_not_url(content: str) -> str:
    not_url_content = RE_MARKDOWN_LINK.sub("", content)
    return f"{not_url_content[:50]}..." if len(not_url_content) > 50 else not_url_content


def content_top_img(content: str) -> str:
    if not content:
        return ""
    img_urls = RE_IMAGE_URL.findall(content)

    if not img_urls:
        return ""

    img_split = img_urls[0].split(RIST_SPLIT)
    if len(img_split) == 2:
        return s3_url(img_split[1])

    return ""
