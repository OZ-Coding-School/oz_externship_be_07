from typing import Any

from drf_spectacular.utils import extend_schema
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
        summary="어드민 답변 삭제",
        description="특정 답변을 삭제하며, 해당 답변에 달린 댓글들도 함께 삭제된 개수를 반환합니다.",
        responses={200: AdminAnswerDeleteSerializer},
        tags=["Admin_qna"],
    )
    def delete(self, request: Request, answer_id: int, *args: Any, **kwargs: Any) -> Response:
        service = AdminAnswerDeleteService()
        result = service.delete_answer(answer_id=answer_id)

        serializer = AdminAnswerDeleteSerializer(result)

        return Response(serializer.data, status=status.HTTP_200_OK)
