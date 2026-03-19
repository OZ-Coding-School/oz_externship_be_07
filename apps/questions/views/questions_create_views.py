from typing import Any, cast

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
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
        description="카테고리 ID, 제목, 내용, 선택적 이미지url 리시트를 입력해야 질문이 등록됩니다.",
        request=QuestionCreateSerializer,
        responses={201: QuestionCreateResponseSerializer},
    )
    def post(self, request: Request) -> Response:
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

        except ValueError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"error_detail": "알 수 없는 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
