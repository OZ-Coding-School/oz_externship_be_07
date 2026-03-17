from typing import Any

from django_redis import get_redis_connection  # type: ignore
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.community.serializers.comment_serializers import (
    PostCommentUserSearchSerializer,
)
from apps.community.services.user_search import UserSearchService


class UserSearchAPIView(GenericAPIView[Any]):
    serializer_class = PostCommentUserSearchSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="댓글 태그",
        description="댓글 태그 기능",
        tags=["posts"],
    )
    def get(self, request: Request) -> Response:
        nickname = request.query_params.get("nickname", "")

        results = UserSearchService.search_users(nickname)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
