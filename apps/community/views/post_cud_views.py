from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers.post_cud_serializers import PostSerializer


class PostCreate(APIView):
    permission_classes = [AllowAny]
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, JSONParser]

    @extend_schema(tags=["PostCreate"], summary="게시판 등록 API", description="커뮤니 게시글 작성 API")
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        mock_data = {
            "detail": "게시글이 성공적으로 등록되었습니다.",
            "id": "1",
        }

        return Response(mock_data, status=status.HTTP_201_CREATED)


class PostDetailUpdateDelete(APIView):
    permission_classes = [AllowAny]
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, JSONParser]

    @extend_schema(
        tags=["PostUpdate"], summary="게시판 수정 API", request=PostSerializer, description="커뮤니티 게시글 수정 API"
    )
    def put(self, request: Request, post_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)

        mock_data = {
            "id": post_id,
            "title": request.data.get("title", "기본 제목"),
            "content": request.data.get("content", "기본 내용"),
            "category": request.data.get("title", "기본 카테고리"),
        }

        return Response(mock_data, status=status.HTTP_200_OK)

    @extend_schema(tags=["PostDelete"], summary="게시판 삭제 API", description="커뮤니티 게시글 삭제 API")
    def delete(self, request: Request, post_id: int) -> Response:
        return Response(status=status.HTTP_204_NO_CONTENT)
