from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


# 질문 등록
@extend_schema(tags=["qna"], summary="질문 등록", description="질문등록 작성 API")
class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """질문등록 MOCK"""
        # 성공 데이터
        success_data = {"message": "질문이 성공적으로 등록되었습니다.", "question_id": 10501}

        # 실패 데이터
        error = {
            "400": {"error_detail": "유효하지 않은 질문 등록 요청입니다."},
            "401": {"error_detail": "로그인한 수강생만 질문을 등록할 수 있습니다."},
            "403": {"error_detail": "질문 등록 권한이 없습니다."},
        }

        return Response(success_data, status=status.HTTP_201_CREATED)

        # 실패 테스트를 하고 싶을때는 아래 주석풀고 성공 리턴에 주석달기!
        # return Response(error["400"], status=status.HTTP_400_BAD_REQUEST])
