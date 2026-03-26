from typing import cast

from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.questions.serializers.questions_serializers import (
    QuestionCreateResponseSerializer,
    QuestionCreateSerializer,
)
from apps.questions.services.questions_create_services import QuestionCreateService
from apps.users.models.models import User


# 질문 등록
class QuestionCreateView:
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionCreateSerializer

    @staticmethod
    def create_question(request: Request) -> Response:
        # 검증
        serializer = QuestionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = cast(User, request.user)

        try:
            new_question = QuestionCreateService.create_question(
                user=user,
                category_id=serializer.validated_data["category_id"],
                title=serializer.validated_data["title"],
                content=serializer.validated_data["content"],
            )

            response_serializer = QuestionCreateResponseSerializer(new_question)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # 카테고리 계층 오류 및 비즈니스 제약 위반
        except (ValidationError, ValueError) as e:
            error_msg = e.detail if hasattr(e, "detail") else str(e)
            return Response({"error_detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        # 권한 부족
        except PermissionDenied as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
