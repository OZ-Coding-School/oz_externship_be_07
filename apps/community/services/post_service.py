from typing import Any, cast

from django.db.models import Count, OuterRef, Q, QuerySet, Subquery

from apps.community.models.post_model import Post, PostImage


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
        "content": post.content,
        "view_count": post.view_count,
        "like_count": post.like_count,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }

extend_schema_200 = OpenApiExample(
    "Ok",
    value={
        "id": 1,
        "title": "게시글 1번 수정",
        "content": "수정된 게시글 본문입니다. 마크다운 허용",
        "category": "테스트 게시판",
    },
    response_only=True,
    status_codes=["200"],
)
extend_schema_201 = OpenApiExample(
    "Ok",
    value={"detail": "게시글이 성공적으로 등록되었습니다.", "pk": 1},
    response_only=True,
    status_codes=["201"],
)
extend_schema_400 = OpenApiExample(
    "Bad Request",
    value={
        "error_detail": {
            "title": ["이 필드는 필수 항목입니다."],
        }
    },
    response_only=True,
    status_codes=["400"],
)
extend_schema_401 = OpenApiExample(
    "Unauthorized",
    value={
        "error_detail": "자격 인증 데이터가 제공되 않았습니다.",
    },
    response_only=True,
    status_codes=["401"],
)

extend_schema_403 = OpenApiExample(
    "Forbidden",
    value={"error_detail": "권한이 없습니다."},
    response_only=True,
    status_codes=["403"],
)
extend_schema_404 = OpenApiExample(
    "Not Found", value={"error_detail": "해당 게시글을 찾을 수 없습니다."}, status_codes=["404"], response_only=True,
)
extend_schema_200_delete = OpenApiExample("OK", value={"detail": "게시글이 삭제되었습니다."}, status_codes=["200"], response_only=True,)


def post_create(request: Request, serializer_class: Type[Any]) -> Response:
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save(author=request.user)

    data = {
        "detail": "게시글이 성공적으로 등록되었습니다.",
        "pk": instance.pk,
    }
    return Response(data, status=status.HTTP_201_CREATED)


def post_put(post_id: int, request: Request, serializer_class: Type[Any]) -> Response:
    try:
        instance = get_object_or_404(Post, pk=post_id)
    except Http404:
        data = {"error_detail": "해당 게시글을 찾을 수 없습니다."}
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if instance.author.pk != request.user.pk:
        data = {"error_detail": "권한이 없습니다."}
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    serializer = serializer_class(instance, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data = {
        "title": request.data["title"],
        "content": request.data["content"],
        "category_id": request.data["category"],
    }
    return Response(data, status=status.HTTP_200_OK)


def post_delete(post_id: int, request: Request) -> Response:
    try:
        instance = get_object_or_404(Post, pk=post_id)
    except Http404:
        data = {"error_detail": "해당 게시글을 찾을 수 없습니다."}
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if instance.author.pk != request.user.pk:
        data = {"error_detail": "권한이 없습니다."}
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    instance.delete()
    data = {"detail": "게시글이 삭제되었습니다."}
    return Response(data, status=status.HTTP_200_OK)
