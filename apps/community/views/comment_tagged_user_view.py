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
from apps.users.models.models import User


class UserSearchAPIView(GenericAPIView["User"]):
    serializer_class = PostCommentUserSearchSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="댓글 태그",
        description="댓글 태그 기능",
        tags=["posts"],
    )
    def get(self, request: Request) -> Response:
        search_query = request.query_params.get("nickname", "")

        if not search_query:
            return Response([], status=status.HTTP_200_OK)

        redis_conn = get_redis_connection("user_search")

        list_results = redis_conn.execute_command(
            "ZRANGEBYLEX", "user_search", f"[{search_query}", f"[{search_query}\xff"
        )

        results = []
        for encoded_byte in list_results:
            decoded_byte = encoded_byte.decode("utf-8")

            try:
                parts = decoded_byte.split(":", 2)
                if len(parts) == 3:
                    nickname, user_id, profile_img_url = parts
                    results.append({"id": int(user_id), "nickname": nickname, "profile_img_url": profile_img_url})
            except ValueError:
                continue

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
