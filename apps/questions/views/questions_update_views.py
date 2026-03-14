from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


# 수정
@extend_schema(tags=["qna"], summary="질문 수정", description="질문 수정 API")
class QuestionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """질문 수정 MOCK"""
        mock_data = {"question_id": 10501, "updated_at": "2025-03-02 14:14:22"}

        error_data = {
            "400": {"error_detail": "유효하지 않은 질문 수정 요청입니다."},
            "401": {"error_detail": "로그인한 사용자만 질문을 수정할 수 있습니다."},
            "403": {"error_detail": "본인이 작성한 질문만 수정할 수 있습니다."},
            "404": {"error_detail": "해당 질문을 찾을 수 없습니다."},
        }

        return Response(mock_data, status=status.HTTP_200_OK)

        # 실패 테스트를 하고 싶을때는 아래 주석풀고 성공 리턴에 주석달기!
        # return Response(error["404"], status=status.HTTP_404_NOT_FOUND)
