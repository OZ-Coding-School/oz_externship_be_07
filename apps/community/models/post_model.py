from django.db import models

from apps.core.models import TimeStampModel


class Post(TimeStampModel):
    """게시글"""

    title = models.CharField(max_length=50, null=False, verbose_name="게시글 제목")
    content = models.TextField(null=False, verbose_name="게시글 내용")
    view_count = models.PositiveIntegerField(default=0, null=False, verbose_name="게시글 조회수")
    is_visible = models.BooleanField(default=True, null=False, verbose_name="게시글 활성화 여부")
    is_notice = models.BooleanField(default=False, null=False, verbose_name="게시글 공지 활성화 여부")
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="posts", verbose_name="작성자")
    category = models.ForeignKey(
        "community.PostCategory", on_delete=models.PROTECT, null=False, related_name="posts", verbose_name="카테고리"
    )

    class Meta:
        db_table = "posts"
        indexes = [
            models.Index(fields=["author"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["category"]),
        ]


class PostAttachment(models.Model):
    """첨부파일"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False, verbose_name="게시판id")
    file_url = models.CharField(max_length=255, null=False, verbose_name="첨부파일 URL")
    file_name = models.CharField(max_length=50, null=False, verbose_name="첨부파일 이름")

    class Meta:
        db_table = "post_attachments"
        verbose_name = "첨부파일"
        verbose_name_plural = "첨부파일 목록"
        indexes = [models.Index(fields=["post"], name="idx_post_attachments_post_id")]


class PostImage(TimeStampModel):
    """이미지"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False, verbose_name="게시판id")
    img_url = models.TextField(null=False, verbose_name="이미지 URL")

    class Meta:
        db_table = "post_images"
        verbose_name = "이미지"
        verbose_name_plural = "이미지 목록"
        indexes = [models.Index(fields=["post"], name="idx_post_images_post_id")]


class PostLike(TimeStampModel):
    """게시글 좋아요"""

    is_liked = models.BooleanField(
        default=True,
        null=False,
        verbose_name="좋아요 여부",
        help_text="T: 좋아요 활성화, F: 좋아요 비활성화",
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=False,
        related_name="post_likes",
        verbose_name="유저",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=False,
        related_name="likes",
        verbose_name="게시글",
    )

    class Meta:
        db_table = "post_likes"
        verbose_name = "게시글 좋아요"
        indexes = [
            models.Index(fields=["post_id"], name="idx_post_like_id"),
        ]
