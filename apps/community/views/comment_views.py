from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from apps.community.core.permissions import IsSelfOrReadOnly
from apps.community.models import PostComment
from apps.community.serializers.comment_serializers import PostCommentSerializer
from apps.community.services.comment_service import CommentService


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet["PostComment"],
):
    serializer_class = PostCommentSerializer
    queryset = PostComment.objects.select_related("author").all()
    permission_classes = [IsSelfOrReadOnly]
    pagination_class = PageNumberPagination

    lookup_field = "id"
    lookup_url_kwarg = "comment_id"

    @extend_schema(
        summary="댓글 목록",
        description="특정 게시글의 모든 댓글 list",
        tags=["Posts"],
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                required=False,
                description="정렬 순서 (recent: 최신순, old: 오래된순)",
                default="recent",
                enum=["recent", "old"],
            ),
        ],
        examples=[
            OpenApiExample(
                name="댓글 목록 예시",
                description="정상응답 데이터",
                value={
                    "id": 1,
                    "content": "첫 테스트",
                    "author": {
                        "id": 1,
                        "nickname": "테스트",
                        "profile_img_url": "https://example.com/uploads/images/users/profiles/image.png",
                    },
                    "created_at": "2026-03-10T17:00:000",
                    "updated_at": "2026-03-10T18:00:000",
                },
                response_only=True,
            )
        ],
    )
    def list(self, request: Request, post_id: int) -> Response:
        ordering = request.query_params.get("ordering", "recent")
        queryset = CommentService.get_comment_tags(post_id=post_id, ordering=ordering)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="댓글 작성",
        description="댓글 작성 api",
        tags=["Posts"],
        examples=[
            OpenApiExample(
                name="댓글 등록 예시",
                description="정상응답 데이터",
                value={"content": "테스트 댓글"},
            )
        ],
        responses={
            201: OpenApiResponse(description="댓글이 등록되었습니다."),
            400: OpenApiResponse(description="필수 항목 데이터가 빠짐."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            404: OpenApiResponse(description="해당 게시글을 찾을 수 없습니다."),
        },
    )
    def create(self, request: Request, post_id: int) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = CommentService.create_comment_tags(
            post_id=post_id,
            author=request.user,
            content=serializer.validated_data.get("content"),
        )

        return Response(
            {"detail": "댓글이 등록되었습니다.", "data": self.get_serializer(comment).data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="댓글 수정",
        description="댓글 수정 api",
        tags=["Posts"],
        examples=[
            OpenApiExample(
                name="댓글 수정 성공 예시",
                value={"content": "수정 댓글"},
                response_only=True,
            )
        ],
        responses={
            200: OpenApiResponse(description="수정된 데이터 반환"),
            400: OpenApiResponse(description="필수 항목 데이터가 빠짐."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 댓글을 찾을 수 없습니다."),
        },
    )
    def update(self, request: Request, post_id: int, comment_id: int) -> Response:
        comment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_comment = CommentService.update_comment_tags(
            post_id=comment.post_id,
            comment_id=comment.id,
            content=serializer.validated_data.get("content"),
        )

        return Response({"detail": "댓글이 수정되었습니다.", "data": self.get_serializer(updated_comment).data})

    @extend_schema(
        summary="댓글 삭제",
        tags=["Posts"],
        responses={
            200: OpenApiResponse(description="댓글이 삭제되었습니다"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 댓글을 찾을 수 없습니다."),
        },
    )
    def destroy(self, request: Request, post_id: int, comment_id: int) -> Response:
        comment = self.get_object()
        CommentService.delete_comment_tags(
            post_id=comment.post_id,
            comment_id=comment.id,
        )

        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
