from typing import Any, Optional

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.users.models.models import User

from ..models import Answers
from ..serializers.answers_serializers import AnswersSerializer
from ..services.answers_services import AnswerService


class AnswerViewSet(viewsets.ModelViewSet[Answers]):
    serializer_class = AnswersSerializer
    permission_classes = [IsAuthenticated]

    # POST /api/v1/qna/questions/{question_id}/answers
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert isinstance(request.user, User)
        question_id: int = int(self.kwargs["question_id"])
        answer = AnswerService.create_answer(
            user=request.user,
            question_id=int(question_id),
            content=str(request.data.get("content", "")),
            image_urls=request.data.get("image_urls"),
        )
        return Response(
            {
                "answer_id": answer.id,
                "question_id": int(question_id),
                "author_id": request.user.id,
                "created_at": answer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_201_CREATED,
        )

    # PUT /api/v1/qna/answers/{answer_id}
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert isinstance(request.user, User)
        pk: int = int(kwargs["pk"])
        answer = AnswerService.update_answer(
            user=request.user,
            answer_id=pk,
            content=str(request.data.get("content", "")),
            image_urls=request.data.get("image_urls"),
        )
        return Response(
            {"answer_id": answer.id, "updated_at": answer.updated_at.strftime("%Y-%m-%d %H:%M:%S")},
            status=status.HTTP_200_OK,
        )

    # POST /api/v1/qna/answers/{answer_id}/accept
    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request: Request, pk: Optional[int] = None) -> Response:
        assert isinstance(request.user, User)  # ✅
        assert pk is not None
        try:  # PermissionDenied가 그냥 터지면 Django가 {"detail": "..."} 형태로 응답하는데, 명세서는 {"error_detail": "..."}
            answer = AnswerService.accept_answer(user=request.user, answer_id=pk)
            return Response(
                {"question_id": answer.questions.id, "answer_id": answer.id, "is_adopted": True},
                status=status.HTTP_200_OK,
            )
        except PermissionDenied as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    # POST /api/v1/qna/answers/{answer_id}/comments
    @action(detail=True, methods=["post"], url_path="comments")
    def comment(self, request: Request, pk: Optional[int] = None) -> Response:
        assert isinstance(request.user, User)
        assert pk is not None
        try:  # ValidationError가 터지면 Django가 ["댓글 내용..."] 리스트 형태로 응답하는데, 명세서는 {"error_detail": "..."} 딕셔너리
            comment = AnswerService.create_comment(
                user=request.user,
                answer_id=pk,
                content=str(request.data.get("content", "")),
            )
            return Response(
                {
                    "comment_id": comment.id,
                    "answer_id": pk,
                    "author_id": request.user.id,
                    "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            errors = e.detail
            error_msg = str(errors[0]) if isinstance(errors, list) else str(errors)  # list/dict 둘 다 처리
            return Response({"error_detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)

    # GET /api/v1/qna/questions/{question_id}/ai-answer
    def get_ai_answer(self, request: Request, question_id: Optional[int] = None) -> Response:
        assert question_id is not None
        try:
            ai_answer = AnswerService.get_or_create_ai_answer(question_id)
            return Response(
                {
                    "id": ai_answer.id,
                    "question_id": ai_answer.questions.id,
                    "output": ai_answer.output,
                    "using_model": ai_answer.using_model,
                    "created_at": ai_answer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            # 명세서 에러 코드 (404, 409)
            status_code: int = status.HTTP_400_BAD_REQUEST
            error_msg = str(e)
            if "이미 AI가 답변" in error_msg:
                status_code = status.HTTP_409_CONFLICT
            elif "찾을 수 없습니다" in error_msg:
                status_code = status.HTTP_404_NOT_FOUND
            return Response({"error_detail": error_msg}, status=status_code)
