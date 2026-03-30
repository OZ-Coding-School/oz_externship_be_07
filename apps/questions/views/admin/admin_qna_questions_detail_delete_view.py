from typing import Any

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
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


class AdminQuestionDetailDeleteCombinedView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="어드민 질의응답 삭제",
        responses={
            200: AdminQuestionDeleteSerializer,
            400: OpenApiResponse(
                examples=[OpenApiExample("400", value={"error_detail": "유효하지 않은 삭제 요청입니다."})]
            ),
            401: OpenApiResponse(examples=[OpenApiExample("401", value={"error_detail": "로그인이 필요합니다."})]),
            403: OpenApiResponse(
                examples=[OpenApiExample("403", value={"error_detail": "질의응답 삭제 권한이 없습니다."})]
            ),
            404: OpenApiResponse(
                examples=[OpenApiExample("404", value={"error_detail": "삭제할 질문을 찾을 수 없습니다."})]
            ),
        },
        tags=["Admin_qna"],
    )
    def delete(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        service = AdminQuestionDeleteService()
        result = service.delete_question(user=request.user, question_id=question_id)
        serializer = AdminQuestionDeleteSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
