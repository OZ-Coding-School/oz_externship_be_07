from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.models import AnswerComments, Answers


class AdminAnswerDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="어드민 답변 삭제",
        tags=["Admin_qna"],
        responses={
            200: OpenApiResponse(description="답변 삭제 성공"),
            401: OpenApiResponse(description="로그인이 필요합니다."),
            403: OpenApiResponse(description="답변 삭제 권한이 없습니다."),
            404: OpenApiResponse(description="삭제할 답변을 찾을 수 없습니다."),
        },
    )
    @transaction.atomic
    def delete(self, request: Request, answer_id: int) -> Response:
        try:
            answer = Answers.objects.get(id=answer_id)
        except Answers.DoesNotExist:
            raise NotFound({"error_detail": "삭제할 답변을 찾을 수 없습니다."})

        deleted_comment_count = AnswerComments.objects.filter(answer=answer).count()
        answer.delete()

        return Response(
            {
                "answer_id": answer_id,
                "deleted_comment_count": deleted_comment_count,
            },
            status=status.HTTP_200_OK,
        )
