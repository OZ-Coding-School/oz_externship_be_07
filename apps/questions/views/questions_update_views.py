from typing import Any, cast

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.models import Questions
from apps.questions.serializers.questions_serializers import (
    QuestionUpdateResponseSerializer,
    QuestionUpdateSerializer,
)
from apps.questions.services.questions_update_services import QuestionUpdateService
from apps.users.models.models import User


# 수정
class QuestionUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionUpdateSerializer

    @extend_schema(
        tags=["questions"],
        summary="질문 수정",
        description="본인이 작성한 질문을 수정합니다.",
        request=QuestionUpdateSerializer,
        responses={200: QuestionUpdateResponseSerializer},
    )
    def put(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        # 시리얼라이저 검증
        serializer = QuestionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 타입 안전성을 위한 유저 캐스팅
        user = cast(User, request.user)

        validated_data = serializer.validated_data

        try:
            # 서비스 호출
            updated_question = QuestionUpdateService.get_question_update(
                question_id=question_id,
                user=user,
                title=validated_data.get("title"),
                content=validated_data.get("content"),
                category_id=validated_data.get("category_id"),
                image_urls=validated_data.get("image_urls"),
            )
            response_serializer = QuestionUpdateResponseSerializer(updated_question)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            return Response(
                {"error_detail": str(e) or "질문을 수정할 권한이 없거나 오류가 발생했습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Questions.DoesNotExist as e:
            return Response({"error_detail": "존재하지 않는 질문입니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error_detail": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
