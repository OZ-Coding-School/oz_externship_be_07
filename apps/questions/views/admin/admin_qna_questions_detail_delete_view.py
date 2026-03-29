from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_questions_detail_delete_serializers import (
    AdminQuestionDeleteSerializer,
)
from apps.questions.services.admin.admin_qna_questions_detail_delete_services import (
    AdminQuestionDeleteService,
)


class AdminQuestionDeleteView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="어드민 질의응답 삭제",
        responses={200: AdminQuestionDeleteSerializer},
        tags=["Admin_qna"],
    )
    def delete(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        service = AdminQuestionDeleteService()
        result = service.delete_question(question_id)

        serializer = AdminQuestionDeleteSerializer(result)

        return Response(serializer.data, status=status.HTTP_200_OK)
