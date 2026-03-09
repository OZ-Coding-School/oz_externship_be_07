from django.db import models

from apps.core.models import TimeStampModel


class PostCategory(TimeStampModel):
    """게시글 카테고리"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=20,
        null=False,
        verbose_name="카테고리 이름",
        help_text="ex) 전체게시판, 공지사항, 자유게시판, 일상 공유, 개발 지식 공유, 취업 정보 공유, 프로젝트 구인",
    )
    status = models.BooleanField(
        default=True, null=False, verbose_name="카테고리 사용 여부", help_text="T: 사용, F: 미사용"
    )

    class Meta:
        db_table = "post_category"
        verbose_name = "게시글 카테고리"
        indexes = [
            models.Index(fields=["id"], name="pk_post_category"),
        ]
