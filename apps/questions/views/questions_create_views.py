from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
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
        tags=["Questions"],
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

        # 카테고리 계층 오류 및 비즈니스 제약 위반
        except (ValidationError, ValueError) as e:
            error_msg = getattr(e, "message", str(e))
            return Response({"error_detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        # 권한 부족
        except PermissionDenied as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        # 예상치 못한 서버 에러
        except Exception:
            return Response(
                {"error_detail": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
