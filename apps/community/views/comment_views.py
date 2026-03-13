from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from apps.community.core.permissions import IsSelfOrReadOnly
from apps.community.models import PostComment
from apps.community.serializers.comment_serializers import PostCommentSerializer


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
        tags=["posts"],
        examples=[
            OpenApiExample(
                name="댓글 목록 예시",
                description="정상응답 데이터",
                value={
                    "count": 254,
                    "next": "https://api.example.com/posts/1/comments/?page=3",
                    "previous": "https://api.example.com/posts/1/comments/?page=1",
                    "results": [
                        {
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
                    ],
                },
                response_only=True,
            )
        ],
    )
    def list(self, request: Request, post_id: int) -> Response:
        queryset = PostComment.objects.filter(post_id=post_id).select_related("author").all()
        page = self.paginate_queryset(queryset)

        if isinstance(page, list):
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response({"error_detail": "해당 게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="댓글 작성",
        description="댓글 작성 api",
        tags=["posts"],
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
        # Todo: 태그된 닉네임 테이블등록
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, post_id=post_id)

        return Response({"detail": "댓글이 등록되었습니다."}, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="댓글 수정",
        description="댓글 수정 api",
        tags=["posts"],
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

        return Response({}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="댓글 삭제",
        tags=["posts"],
        responses={
            200: OpenApiResponse(description="댓글이 삭제되었습니다"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 댓글을 찾을 수 없습니다."),
        },
    )
    def destroy(self, request: Request, post_id: int, comment_id: int) -> Response:

        return Response({}, status=status.HTTP_200_OK)
