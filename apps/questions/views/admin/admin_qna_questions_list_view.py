from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.models import AnswerComments, Answers, Questions
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

    @extend_schema(
        summary="어드민 질의응답 삭제",
        tags=["Admin_qna"],
        responses={
            200: OpenApiResponse(description="질문 삭제 성공"),
            401: OpenApiResponse(description="로그인이 필요합니다."),
            403: OpenApiResponse(description="질의응답 삭제 권한이 없습니다."),
            404: OpenApiResponse(description="삭제할 질문을 찾을 수 없습니다."),
        },
    )
    @transaction.atomic
    def delete(self, request: Request, question_id: int) -> Response:
        try:
            question = Questions.objects.get(id=question_id)
        except Questions.DoesNotExist:
            raise NotFound({"error_detail": "삭제할 질문을 찾을 수 없습니다."})

        answers = Answers.objects.filter(questions=question)
        deleted_answer_count = answers.count()
        deleted_comment_count = AnswerComments.objects.filter(answer__in=answers).count()

        question.delete()

        return Response(
            {
                "question_id": question_id,
                "deleted_answer_count": deleted_answer_count,
                "deleted_comment_count": deleted_comment_count,
            },
            status=status.HTTP_200_OK,
        )
