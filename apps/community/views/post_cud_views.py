from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post
from apps.community.serializers.post_cud_serializers import (
    PostCreateSerializer,
    PostUpdateSerializer,
)

common_error = [
    OpenApiExample(
        "Bad Request",
        value={
            "error_detail": {
                "title": ["이 필드는 필수 항목입니다."],
            }
        },
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        "Unauthorized",
        value={
            "error_detail": "자격 인증 데이터가 제공되 않았습니다.",
        },
        response_only=True,
        status_codes=["401"],
    ),
]


class PostCreate(APIView):
    permission_classes = [AllowAny]
    serializer_class = PostCreateSerializer
    parser_classes = [MultiPartParser, JSONParser]

    @extend_schema(
        tags=["posts"],
        summary="게시판 등록",
        description="커뮤니 게시글 작성 API",
        examples=[
            OpenApiExample(
                "Ok",
                value={"detail": "게시글이 성공적으로 등록되었습니다.", "pk": 1},
                status_codes=["201"],
            ),
        ]
        + common_error,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        mock_data = {
            "detail": "게시글이 성공적으로 등록되었습니다.",
            "pk": "1",
        }

        return Response(mock_data, status=status.HTTP_201_CREATED)


class PostDetailUpdateDelete(APIView):
    permission_classes = [AllowAny]
    serializer_class = PostUpdateSerializer
    parser_classes = [MultiPartParser, JSONParser]

    @extend_schema(
        tags=["posts"],
        summary="게시판 수정",
        request=PostUpdateSerializer,
        description="커뮤니티 게시글 수정 API",
        examples=[
            OpenApiExample(
                "Ok",
                value={
                    "id": 1,
                    "title": "게시글 1번 수정",
                    "content": "수정된 게시글 본문입니다. 마크다운 허용",
                    "category_id": 2,
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Forbidden",
                value={"error_detail": "권한이 없습니다."},
                response_only=True,
                status_codes=["403"],
            ),
            OpenApiExample(
                "Not Found",
                value={"error_detail": "해당 게시글을 찾을 수 없습니다."},
                response_only=True,
                status_codes=["404"],
            ),
        ]
        + common_error,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def put(self, request: Request, post_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)

        mock_data = {
            "id": post_id,
            "title": request.data.get("title", "기본 제목"),
            "content": request.data.get("content", "기본 내용"),
            "category_id": request.data.get("category", 1),
        }

        return Response(mock_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["posts"],
        summary="게시판 삭제",
        description="커뮤니티 게시글 삭제 API",
        examples=[
            OpenApiExample(
                "OK", value={"detail": "게시글이 삭제되었습니다."}, response_only=True, status_codes=["200"]
            ),
            OpenApiExample(
                "Forbidden",
                value={"error_detail": "권한이 없습니다."},
                response_only=True,
                status_codes=["403"],
            ),
            OpenApiExample(
                "Not Found",
                value={"error_detail": "해당 게시글을 찾을 수 없습니다."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def delete(self, request: Request, post_id: int) -> Response:
        post = get_object_or_404(Post, pk=post_id)
        post.delete()
        mock_data = {"detail": "게시글이 삭제되었습니다."}
        return Response(mock_data, status=status.HTTP_200_OK)
