from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_questions_list_serializers import (
    AdminQuestionDetailSerializer,
)
from apps.questions.services.admin.admin_qna_questions_list_services import (
    AdminQuestionDetailService,
)


class AdminQuestionDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="관리자 질의응답 상세 조회",
        responses={200: AdminQuestionDetailSerializer},
        tags=["Admin_qna"],
    )
    def get(self, request: Request, question_id: int) -> Response:
        question = AdminQuestionDetailService.get_question_detail(question_id)

        serializer = AdminQuestionDetailSerializer(question)

        return Response(serializer.data, status=status.HTTP_200_OK)
