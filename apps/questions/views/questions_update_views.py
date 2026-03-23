from typing import cast

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.questions.serializers.questions_serializers import (
    QuestionUpdateResponseSerializer,
    QuestionUpdateSerializer,
)
from apps.questions.services.questions_update_services import QuestionUpdateService
from apps.users.models.models import User


# 수정
class QuestionUpdateView:
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionUpdateSerializer

    @staticmethod
    def update_question(request: Request, question_id: int) -> Response:
        try:
            # 시리얼라이저 검증
            serializer = QuestionUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            # 타입 안전성을 위한 유저 캐스팅
            user = cast(User, request.user)

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

        # 없는 질문 수정할떄 나는 에러
        except Http404:
            return Response({"error_detail": "존재하지 않는 질문입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 수정 권한이 없는 에러
        except PermissionDenied as e:
            return Response(
                {"error_detail": str(e) or "질문을 수정할 권한이 없거나 오류가 발생했습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
