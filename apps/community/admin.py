from django.contrib import admin
from django.http import HttpRequest
from django.utils.text import Truncator

from apps.community.models.category_model import PostCategory
from apps.community.models.comment_model import CommentTag, PostComment
from apps.community.models.post_model import Post, PostAttachment, PostImage, PostLike


class PostImageInline(admin.TabularInline):  # type: ignore[type-arg]
    model = PostImage
    extra = 0
    fields = ("id", "img_url", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    show_change_link = True


class PostAttachmentInline(admin.TabularInline):  # type: ignore[type-arg]
    model = PostAttachment
    extra = 0
    fields = ("id", "file_name", "file_url")
    readonly_fields = ("id",)
    show_change_link = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "title", "author", "view_count", "category", "is_notice", "is_visible", "created_at")
    search_fields = ("title", "content", "author__nickname")
    list_filter = ("category", "is_notice", "is_visible")
    list_select_related = ("author", "category")
    raw_id_fields = ("author",)
    ordering = ("-created_at",)
    inlines = [PostAttachmentInline, PostImageInline]


class CommentTagInline(admin.TabularInline):  # type: ignore[type-arg]
    model = CommentTag
    extra = 0
    fields = ("id", "tagged_user", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("tagged_user",)
    show_change_link = True


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "author", "post", "content_preview", "created_at")
    search_fields = ("content", "author__nickname")
    list_filter = ("post",)
    list_select_related = ("author", "post")
    raw_id_fields = ("author", "post")
    ordering = ("-created_at",)
    inlines = [CommentTagInline]
    @admin.register(PostComment)
    class PostCommentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
        list_display = ("id", "author", "post", "content_preview", "created_at")
        search_fields = ("content", "author__nickname")
        list_filter = ("post",)
        list_select_related = ("author", "post")
        ordering = ("-created_at",)
        inlines = [CommentTagInline]

        @admin.display(description="댓글내용", ordering="content")
        def content_preview(self, obj: PostComment) -> str:
            text = (obj.content or "").replace("\n", " ")
            return Truncator(text).chars(16)


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "name", "status")
    search_fields = ("name",)
    list_filter = ("status",)
    ordering = ("id",)


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "user", "post", "is_liked", "created_at")
    search_fields = ("user__nickname", "post__title")
    list_filter = ("is_liked",)
    list_select_related = ("user", "post")
    ordering = ("-created_at",)
    readonly_fields = ("id", "user", "post", "is_liked", "created_at")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: PostLike | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: PostLike | None = None) -> bool:
        return False
