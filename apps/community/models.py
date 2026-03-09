from django.db import models

class Post(models.Model):
    """게시글"""

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50, null=False, verbose_name= "게시글 제목")
    content = models.TextField(null=False, verbose_name= "게시글 내용")
    view_count = models.PositiveIntegerField(default=0, null=False, verbose_name="게시글 조회수")
    is_visible = models.BooleanField(default=True, null=False, verbose_name="게시글 활성화 여부")
    is_notice = models.BooleanField(default=False, null=False, verbose_name="게시글 공지 활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name="게시글 생성 일시")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="게시글 수정 일시")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="작성자"
    )
    category = models.ForeignKey(
        "community.PostCategory",
        on_delete=models.PROTECT,
        null=False,
        related_name="posts",
        verbose_name="카테고리"
    )

    class Meta:
        db_table = "post"
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["author"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["category"])
        ]

class PostAttachments(models.Model):
    """첨부파일"""

    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False, verbose_name="게시판id")
    file_url = models.CharField(max_length=255, null=False, verbose_name="첨부파일 URL")
    file_name = models.CharField(max_length=50, null=False, verbose_name="첨부파일 이름")

    class Meta:
        verbose_name = "첨부파일"
        verbose_name_plural = "첨부파일 목록"
        indexes = [
            models.Index(fields=["post"], name="idx_post_attachments_post_id")
        ]

    def __str__(self):
        return f"{self.file_name} : {self.file_url}"

class PostImage(models.Model):
    """이미지"""
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False, verbose_name="게시판id")
    img_url = models.TextField(null=False, verbose_name="이미지 URL")
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name="작성일시")
    updated_at = models.DateTimeField(null=True, verbose_name="수정일시")

    class Meta:
        verbose_name = "이미지"
        verbose_name_plural = "이미지 목록"
        indexes = [
            models.Index(fields=["post"], name="idx_post_images_post_id")
        ]

    def __str__(self):
        return f"{self.img_url}"


class PostComment(models.Model):
    """댓글"""

    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey('users.User',on_delete=models.CASCADE, null=False, verbose_name="작성자id")
    post = models.ForeignKey('Post',on_delete=models.CASCADE, null=False, verbose_name="게시글id")
    content = models.CharField(max_length=300, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        table_name = 'post_comment'
        indexes = [
            models.Index(fields=['post','created_at'], name='idx_post_id|created_at'),
        ]

class CommentTag(models.Model):
    """태그된 ID 저장"""

    id = models.BigAutoField(primary_key=True)
    tagged_user = models.ForeignKey('users.User',on_delete=models.CASCADE, null=False)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        table_name = 'post_comment_tags'
        indexes = [
            models.Index(fields=['tagged_user'], name='idx_tagged_user_id'),
        ]

class PostCategory(models.Model):
    """게시글 카테고리"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=20, null=False, verbose_name="카테고리 이름",
        help_text="ex) 전체게시판, 공지사항, 자유게시판, 일상 공유, 개발 지식 공유, 취업 정보 공유, 프로젝트 구인"
    )
    status = models.BooleanField(
        default=True,
        null=False,
        verbose_name="카테고리 사용 여부",
        help_text="T: 사용, F: 미사용"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name="생성 일시")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="수정 일시")

    class Meta:
        table_name = 'post_category',
        verbose_name = "게시글 카테고리"
        indexes = [
            models.Index(fields=["id"], name="pk_post_category"),
        ]

    def __str__(self):
        return self.name


class PostLike(models.Model):
    """게시글 좋아요"""
    id = models.BigAutoField(primary_key=True)
    is_liked = models.BooleanField(
        default=False,
        null=False,
        verbose_name="좋아요 여부",
        help_text="T: 좋아요 활성화, F: 좋아요 비활성화",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name="좋아요 생성일시")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="좋아요 수정일시")

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=False,
        db_column="user",
        related_name="post_likes",
        verbose_name="유저",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=False,
        db_column="post",
        related_name="likes",
        verbose_name="게시글",
    )

    class Meta:
        table_name = 'pos_like'
        verbose_name = "게시글 좋아요"
        indexes = [
            models.Index(fields=["post_id"], name="idx_post_like_id"),
        ]

    def __str__(self):
        return f"Postlike(post_id={self.post_id}, user_id={self.user_id}, is_liked={self.is_liked})"







