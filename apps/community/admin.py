from typing import Any, cast
from urllib.parse import urlparse

from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.text import Truncator

from apps.community.models.category_model import PostCategory
from apps.community.models.comment_model import CommentTag, PostComment
from apps.community.models.post_model import Post, PostAttachment, PostImage, PostLike


def _is_safe_external_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


class PostImageInline(admin.TabularInline):  # type: ignore[type-arg]
    model = PostImage
    extra = 0
    fields = ("id", "image_thumbnail", "img_url", "created_at", "updated_at")
    readonly_fields = ("id", "image_thumbnail", "created_at", "updated_at")
    show_change_link = True

    @admin.display(description="미리보기")
    def image_thumbnail(self, obj: PostImage) -> str:
        if not obj.img_url or not _is_safe_external_url(obj.img_url):
            return "-"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">'
            '<img src="{}" alt="preview" loading="lazy" '
            'style="max-width:90px;max-height:90px;object-fit:cover;border:1px solid #ddd;border-radius:4px;" />'
            "</a>",
            obj.img_url,
            obj.img_url,
        )


class PostAttachmentInline(admin.TabularInline):  # type: ignore[type-arg]
    model = PostAttachment
    extra = 0
    fields = ("id", "file_name", "file_download", "file_url")
    readonly_fields = ("id", "file_download")
    show_change_link = True

    @admin.display(description="다운로드")
    def file_download(self, obj: PostAttachment) -> str:
        if not obj.file_url or not _is_safe_external_url(obj.file_url):
            return "-"
        extension = obj.file_name.rsplit(".", 1)[-1].upper() if "." in obj.file_name else "FILE"
        display_name = Truncator(obj.file_name).chars(26)
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer" download>'
            '<span style="background:#334155;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;">{}</span> '
            "{}"
            "</a>",
            obj.file_url,
            extension,
            display_name,
        )


class PostCommentInline(admin.TabularInline):  # type: ignore[type-arg]
    model = PostComment
    extra = 0
    fields = ("id", "author", "content_preview", "created_at")
    readonly_fields = ("id", "author", "content_preview", "created_at")
    raw_id_fields = ("author",)
    show_change_link = True

    @admin.display(description="댓글 내용")
    def content_preview(self, obj: PostComment) -> str:
        text = (obj.content or "").replace("\n", " ")
        return Truncator(text).chars(16)

    def get_queryset(self, request: HttpRequest) -> QuerySet[PostComment]:
        queryset = cast(QuerySet[PostComment], super().get_queryset(request))
        return queryset.select_related("author")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    AUTOCOMPLETE_APP_LABEL = "community"
    AUTOCOMPLETE_MODEL_NAME = "postcomment"
    AUTOCOMPLETE_FIELD_NAME = "post"
    AUTOCOMPLETE_LIMIT = 5

    list_display = (
        "id",
        "title",
        "author",
        "view_count",
        "like_count",
        "category",
        "is_notice",
        "is_visible",
        "created_at",
    )
    list_display_links = ("id", "title")
    list_editable = ("is_notice", "is_visible")
    search_fields = ("title", "content", "author__nickname")
    list_filter = ("category", "is_notice", "is_visible")
    raw_id_fields = ("author",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("like_count", "created_at", "updated_at")
    fieldsets = (
        ("기본 정보", {"fields": ("title", "author", "category")}),
        ("내용", {"fields": ("content",)}),
        ("운영", {"fields": ("view_count", "like_count", "is_notice", "is_visible")}),
        ("일시", {"fields": ("created_at", "updated_at")}),
    )

    def get_fieldsets(self, request: HttpRequest, obj: Post | None = None) -> Any:
        if obj is None:
            return (
                ("기본 정보", {"fields": ("title", "author", "category")}),
                ("내용", {"fields": ("content",)}),
                ("운영", {"fields": ("view_count", "is_notice", "is_visible")}),
            )
        return self.fieldsets

    def _is_postcomment_post_autocomplete_request(self, request: HttpRequest) -> bool:
        return (
            request.path.endswith("/autocomplete/")
            and request.GET.get("app_label") == self.AUTOCOMPLETE_APP_LABEL
            and request.GET.get("model_name") == self.AUTOCOMPLETE_MODEL_NAME
            and request.GET.get("field_name") == self.AUTOCOMPLETE_FIELD_NAME
        )

    def get_search_results(
        self,
        request: HttpRequest,
        queryset: Any,
        search_term: str,
    ) -> tuple[QuerySet[Post], bool]:
        if not self._is_postcomment_post_autocomplete_request(request):
            base_qs, use_distinct = super().get_search_results(request, queryset, search_term)
            return cast(QuerySet[Post], base_qs), use_distinct

        ordered_qs = queryset.order_by("-created_at", "-id")
        keyword = search_term.strip()

        if keyword == "":
            return ordered_qs[: self.AUTOCOMPLETE_LIMIT], False

        return ordered_qs.filter(title__icontains=keyword), False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        queryset = (
            super()
            .get_queryset(request)
            .select_related("author", "category")
            .annotate(like_count_value=Count("likes", filter=Q(likes__is_liked=True), distinct=True))
        )
        return cast(QuerySet[Post], queryset)

    @admin.display(description="좋아요 수", ordering="like_count_value")
    def like_count(self, obj: Post) -> int:
        return int(getattr(obj, "like_count_value", 0))

    def get_deleted_objects(self, objs: Any, request: HttpRequest) -> tuple[Any, Any, Any, Any]:
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)

        warning = "⚠️주의: 게시글 삭제 시 해당 게시글의 댓글이 함께 삭제되며 되돌릴 수 없습니다."
        if warning not in deleted_objects:
            deleted_objects.append(warning)

        return deleted_objects, model_count, perms_needed, protected

    inlines = [PostAttachmentInline, PostImageInline, PostCommentInline]


class CommentTagInline(admin.TabularInline):  # type: ignore[type-arg]
    model = CommentTag
    extra = 0
    fields = ("id", "tagged_user", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("tagged_user",)
    show_change_link = True


class PostCommentPostAutocompleteFilter(AutocompleteFilter):  # type: ignore[misc]
    title = "게시글"
    field_name = "post"


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "author", "post", "content_preview", "created_at")
    search_fields = ("content", "author__nickname", "post__title")
    list_filter = (PostCommentPostAutocompleteFilter,)
    show_facets = admin.ShowFacets.NEVER
    raw_id_fields = ("author", "post")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("기본 정보", {"fields": ("author", "post")}),
        ("내용", {"fields": ("content",)}),
        ("일시", {"fields": ("created_at", "updated_at")}),
    )

    def get_fieldsets(self, request: HttpRequest, obj: PostComment | None = None) -> Any:
        if obj is None:
            return (
                ("기본 정보", {"fields": ("author", "post")}),
                ("내용", {"fields": ("content",)}),
            )
        return self.fieldsets

    def get_queryset(self, request: HttpRequest) -> QuerySet[PostComment]:
        queryset = super().get_queryset(request).select_related("author", "post")
        return cast(QuerySet[PostComment], queryset)

    inlines = [CommentTagInline]

    @admin.display(description="댓글내용", ordering="content")
    def content_preview(self, obj: PostComment) -> str:
        text = (obj.content or "").replace("\n", " ")
        return Truncator(text).chars(16)


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "name", "status")
    list_display_links = ("id", "name")
    list_editable = ("status",)
    search_fields = ("name",)
    list_filter = ("status",)
    ordering = ("id",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("기본 정보", {"fields": ("name", "status")}),
        ("일시", {"fields": ("created_at", "updated_at")}),
    )

    def get_fieldsets(self, request: HttpRequest, obj: PostCategory | None = None) -> Any:
        if obj is None:
            return (("기본 정보", {"fields": ("name", "status")}),)
        return self.fieldsets


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "user", "post", "is_liked", "created_at")
    search_fields = ("user__nickname", "post__title")
    list_filter = ("is_liked",)
    list_select_related = ("user", "post")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("id", "user", "post", "is_liked", "created_at", "updated_at")
    fieldsets = (
        ("기본 정보", {"fields": ("id", "user", "post", "is_liked")}),
        ("일시", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: PostLike | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: PostLike | None = None) -> bool:
        return False
