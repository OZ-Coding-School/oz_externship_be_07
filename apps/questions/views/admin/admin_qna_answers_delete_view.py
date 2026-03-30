from typing import Any

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_answers_delete_serializers import (
    AdminAnswerDeleteSerializer,
)
from apps.questions.services.admin.admin_qna_answers_delete_services import (
    AdminAnswerDeleteService,
)


class AdminAnswerDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="어드민 답변 삭제 API",
        description="특정 답변을 삭제하며, 해당 답변에 달린 댓글들도 함께 삭제된 개수를 반환합니다.",
        responses={
            200: AdminAnswerDeleteSerializer,
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청 예시",
                        value={"error_detail": "유효하지 않은 답변 삭제 요청입니다."},
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "로그인 필요 예시",
                        value={"error_detail": "로그인이 필요합니다."},
                    )
                ],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 부족 예시",
                        value={"error_detail": "답변 삭제 권한이 없습니다."},
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "삭제 대상 미존재 예시",
                        value={"error_detail": "삭제할 답변을 찾을 수 없습니다."},
                    )
                ],
            ),
        },
        tags=["Admin_qna"],
    )
    def delete(self, request: Request, answer_id: int, *args: Any, **kwargs: Any) -> Response:
        service = AdminAnswerDeleteService()

        result = service.delete_answer(user=request.user, answer_id=answer_id)

        serializer = AdminAnswerDeleteSerializer(result)

        return Response(serializer.data, status=status.HTTP_200_OK)
