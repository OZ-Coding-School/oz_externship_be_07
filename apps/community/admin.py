import time
from typing import Any, cast
from urllib.parse import urlparse

from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin, messages
from django.db import transaction
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
    inlines = [PostAttachmentInline, PostImageInline, PostCommentInline]

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

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "category":
            kwargs["queryset"] = PostCategory.objects.filter(status=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_search_results(
        self,
        request: HttpRequest,
        queryset: QuerySet[Post],
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

        warning_message = "⚠️주의: 게시글 삭제 시 해당 게시글의 댓글이 함께 삭제되며 되돌릴 수 없습니다."
        if warning_message not in deleted_objects:
            deleted_objects.append(warning_message)

        return deleted_objects, model_count, perms_needed, protected


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
    inlines = [CommentTagInline]

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

    @admin.display(description="댓글내용", ordering="content")
    def content_preview(self, obj: PostComment) -> str:
        text = (obj.content or "").replace("\n", " ")
        return Truncator(text).chars(16)


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    DELETE_CONFIRM_SESSION_KEY = "community_category_delete_confirm"
    DELETE_CONFIRM_TTL_SECONDS = 180

    list_display = ("id", "name", "status")
    list_display_links = ("id", "name")
    list_editable = ("status",)
    search_fields = ("name",)
    list_filter = ("status",)
    ordering = ("id",)
    readonly_fields = ("created_at", "updated_at")
    actions = ("delete_category_by_policy",)
    fieldsets = (
        ("기본 정보", {"fields": ("name", "status")}),
        ("일시", {"fields": ("created_at", "updated_at")}),
    )

    def get_fieldsets(self, request: HttpRequest, obj: PostCategory | None = None) -> Any:
        if obj is None:
            return (("기본 정보", {"fields": ("name", "status")}),)
        return self.fieldsets

    def save_model(self, request: HttpRequest, obj: PostCategory, form: Any, change: bool) -> None:
        should_warn = False
        hidden_post_count = 0

        if change:
            previous_category = PostCategory.objects.filter(pk=obj.pk).only("status").first()
            if previous_category and previous_category.status and not obj.status:
                hidden_post_count = Post.objects.filter(category_id=obj.pk, is_visible=True).count()
                should_warn = hidden_post_count > 0

        super().save_model(request, obj, form, change)

        if should_warn:
            self.message_user(
                request,
                f"카테고리를 비활성화했습니다. ❗현재 공개 상태 게시글 {hidden_post_count}건은 사용자 화면에서 비노출됩니다.",
                level=messages.WARNING,
            )

    def get_actions(self, request: HttpRequest) -> dict[str, Any]:
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    @admin.action(description="카테고리 상태 및 게시글유무에 따른 삭제 처리")
    def delete_category_by_policy(
        self,
        request: HttpRequest,
        queryset: QuerySet[PostCategory],
    ) -> None:
        selected_ids = sorted(queryset.values_list("id", flat=True))
        now_ts = int(time.time())
        confirm_payload = request.session.get(self.DELETE_CONFIRM_SESSION_KEY)

        if isinstance(confirm_payload, dict):
            ts = confirm_payload.get("ts")
            if ts is None or now_ts - int(ts) > self.DELETE_CONFIRM_TTL_SECONDS:
                request.session.pop(self.DELETE_CONFIRM_SESSION_KEY, None)
                confirm_payload = None

        is_confirmed = (
                isinstance(confirm_payload, dict)
                and confirm_payload.get("ids") == selected_ids
                and now_ts - int(confirm_payload.get("ts", 0)) <= self.DELETE_CONFIRM_TTL_SECONDS
        )

        if not is_confirmed:
            request.session[self.DELETE_CONFIRM_SESSION_KEY] = {
                "ids": selected_ids,
                "ts": now_ts,
            }

            preview_limit = 3
            selected_count = len(selected_ids)
            preview_names = list(queryset.values_list("name", flat=True)[:preview_limit])
            safe_names = [name if name else "(이름 없음)" for name in preview_names]

            if selected_count > preview_limit:
                preview_text = f"{', '.join(safe_names)} 외 {selected_count - preview_limit}개"
            else:
                preview_text = ", ".join(safe_names)

            self.message_user(
                request,
                f"⚠️ 삭제 확인: [{preview_text}] 동일 항목 선택 후 다시 한 번 액션을 실행하면 삭제됩니다. (3분 이내)",
                level=messages.WARNING,
            )
            return

        request.session.pop(self.DELETE_CONFIRM_SESSION_KEY, None)

        deleted_category_count = 0
        deleted_post_count = 0
        blocked_categories: list[str] = []

        for category in queryset:
            post_queryset = Post.objects.filter(category=category)
            post_count = post_queryset.count()

            if category.status and post_count > 0:
                blocked_categories.append(f"{category.name}({post_count}개)")
                continue

            with transaction.atomic():
                if not category.status and post_count > 0:
                    post_queryset.delete()
                    deleted_post_count += post_count

                category.delete()
                deleted_category_count += 1

        if blocked_categories:
            self.message_user(
                request,
                f"활성 카테고리이며 게시글이 있어 삭제하지 않았습니다: " f"{', '.join(blocked_categories)}",
                level=messages.WARNING,
            )

        if deleted_category_count > 0:
            self.message_user(
                request,
                f"삭제 완료: 카테고리 {deleted_category_count}개, 게시글 {deleted_post_count}개",
                level=messages.SUCCESS,
            )


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
        if "/admin/community/post/" in request.path:
            return True
        return False
