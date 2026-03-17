from typing import Any, cast

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.questions_serializers import (
    QuestionCreateResponseSerializer,
    QuestionCreateSerializer,
)
from apps.questions.services.questions_create_services import QuestionCreateService
from apps.users.models.models import User


# 질문 등록
class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    serializer_class = QuestionCreateSerializer

    @extend_schema(
        tags=["qna"],
        summary="질문 등록",
        description="카테고리 ID, 제목, 내용을 입력해야 질문이 등록됩니다.",
        request=QuestionCreateSerializer,
        responses={201: QuestionCreateResponseSerializer},
        examples=[
            # MOCK데이터
            OpenApiExample(
                "성공예시",
                value={"message": "질문이 성공적으로 등록되었습니다.", "question_id": 10501},
                response_only=True,
                status_codes=["201"],
            )
        ],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 검증
        serializer = QuestionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": "입력 값이 유효하지 않습니다.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = cast(User, request.user)

        try:
            new_question = QuestionCreateService.create_question(
                user=user,
                category_id=serializer.validated_data["category_id"],
                title=serializer.validated_data["title"],
                content=serializer.validated_data["content"],
                image_url_list=serializer.validated_data.get("image_urls"),
            )

            response_serializer = QuestionCreateResponseSerializer(new_question)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
