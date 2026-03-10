from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiExample
from typing import Any
from rest_framework import mixins, viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.community.models import PostComment

# from apps.community.permissions import IsSelfOrReadOnly
from apps.community.serializers.comment_serializers import PostCommentSerializer


# class CommentViewSet(viewsets.ModelViewSet):
class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet["PostComment"],
):
    serializer_class = PostCommentSerializer
    queryset = PostComment.objects.select_related("author").all()
    # Todo: 권한설정 예정
    # permission_classes = [IsSelfOrReadOnly]

    lookup_field = "id"
    lookup_url_kwarg = "comment_id"

    @extend_schema(
        summary="댓글 목록",  # api 제목
        description="특정 게시글의 모든 댓글 list",  # 설명
        tags=["Community - Comments"],  # api를 기능별로 묶어준다
        responses={200: PostCommentSerializer},  # 성공 및 실패 명세
        examples=[
            OpenApiExample(
                name="댓글 목록 예시",
                description="정상응답 데이터",
                value=[
                    {
                        "id": 1,
                        "content": "첫 테스트",
                        "author": "테스트",
                        "created_at": "2026-03-10T17:00:000"
                    },
                    {
                        "id": 2,
                        "content": "두번쨰 테스트",
                        "author": "테스트",
                        "created_at": "2026-03-10T17:05:000"
                    }
                ],
                response_only=True,
            )
        ]
    )
    def list(self, request: Request, post_id: int) -> Response:
        """
        GET api/v1/posts/{post_id}/comments
        커뮤니티 댓글 작성 api
        :param request: 요청객체
        :return: 댓글 객체 반환
        """
        return Response([], status=status.HTTP_200_OK)

    @extend_schema(
        summary="댓글 작성",  # api 제목
        description="댓글 작성 api",  # 설명
        tags=["Community - Comments"],  # api를 기능별로 묶어준다
        examples=[
            OpenApiExample(
                name="댓글 작성 성공 예시",
                value={
                    "id": 10,
                    "content": "테스트 댓글",
                    "author": "테스트",
                    "created_at": "2026-03-10T17:30:000"
                },
                response_only=True,
                status_codes=["201"]
            )
        ],
        responses={
            201: PostCommentSerializer,
            400: OpenApiResponse(description="요청이 잘못되었습니다"),
            401: OpenApiResponse(description="권한이 없습니다"),
            403: OpenApiResponse(description="권한이외의 이유로 접근이 금지되었습다"),
            404: OpenApiResponse(description="알 수 없는 이유로 생성 실패"),
        },  # 성공 및 실패 명세
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        POST api/v1/posts/{post_id}/comments
        커뮤니티 게시 댓글 작성 api
        :param serializer:댓글 serializers
        :return: 생성 객체 반환
        """
        return Response([], status=status.HTTP_200_OK)

    # def perform_create(self, serializer: PostCommentSerializer) -> None:
    #     post_id = self.kwargs.get('post_id')
    #     serializer.save(
    #         author=self.request.user,
    #         post_id=post_id
    #     )

    @extend_schema(
        summary="댓글 수정",  # api 제목
        description="댓글 수정 api",  # 설명
        tags=["Community - Comments"],
        examples=[
            OpenApiExample(
                name="댓글 수정 성공 예시",
                value={
                    "id": 5,
                    "content": "수정 댓글",
                    "author": "테스트",
                    "updated_at": "2026-03-10T18:00:000"
                },
                response_only=True,
                status_codes=["200"]
            )
        ],
        responses={
            201: OpenApiResponse(description="수정 성공"),
            400: OpenApiResponse(description="요청이 잘못되었습니다"),
            401: OpenApiResponse(description="권한이 없습니다"),
            403: OpenApiResponse(description="권한이외의 이유로 접근이 금지되었습다"),
            404: OpenApiResponse(description="알 수 없는 이유로 수정 실패"),
        },
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        PUT api/v1/posts/{post_id}/comments/{comment_id}
        커뮤니티 게시글 댓글 수정 api
        :param request: 수정 데이터 객체
        :return: 수장된 데이터 객체
        """
        return Response([], status=status.HTTP_200_OK)

    @extend_schema(
        summary="댓글 삭제",
        tags=["Community - Comments"],
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            400: OpenApiResponse(description="요청이 잘못되었습니다"),
            401: OpenApiResponse(description="권한이 없습니다"),
            403: OpenApiResponse(description="권한이외의 이유로 접근이 금지되었습다"),
            404: OpenApiResponse(description="알 수 없는 이유로 삭제 실패"),
        },
    )
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        DELETE api/v1/posts/{post_id}/comments/{comment_id}
        커뮤니티 게시글 댓글 삭제 api
        :param request: 삭제요청 객체
        :return: None
        """
        return Response(status=status.HTTP_204_NO_CONTENT)
