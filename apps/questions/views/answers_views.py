from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.users.models.models import User

from ..serializers.answers_serializers import (
    AnswerCreateUpdateSerializer,
    CommentCreateSerializer,
)
from ..services.answers_services import AnswerService


class AnswerViewSet(viewsets.GenericViewSet[Any]):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> type:
        if self.action == "comment":
            return CommentCreateSerializer
        return AnswerCreateUpdateSerializer

    # 답변 등록
    @extend_schema(
        tags=["Qna"],
        summary="답변 등록",
        request=AnswerCreateUpdateSerializer,
        responses={
            201: OpenApiResponse(description="답변 등록 성공"),
            400: OpenApiResponse(description="유효하지 않은 답변 등록 요청입니다."),
            401: OpenApiResponse(description="로그인한 사용자만 답변을 작성할 수 있습니다."),
            403: OpenApiResponse(description="답변 작성 권한이 없습니다."),
            404: OpenApiResponse(description="해당 질문을 찾을 수 없습니다."),
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert isinstance(request.user, User)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = AnswerService.create_answer(
            user=request.user,
            question_id=int(self.kwargs["question_id"]),
            **serializer.validated_data,
        )
        return Response(
            {
                "answer_id": answer.id,
                "question_id": answer.questions.id,
                "author_id": request.user.id,
                "created_at": answer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_201_CREATED,
        )

    # 답변 수정
    @extend_schema(
        tags=["Qna"],
        summary="답변 수정",
        request=AnswerCreateUpdateSerializer,
        responses={
            200: OpenApiResponse(description="답변 수정 성공"),
            400: OpenApiResponse(description="유효하지 않은 답변 수정 요청입니다."),
            401: OpenApiResponse(description="로그인한 사용자만 답변을 수정할 수 있습니다."),
            403: OpenApiResponse(description="본인이 작성한 답변만 수정할 수 있습니다."),
            404: OpenApiResponse(description="해당 답변을 찾을 수 없습니다."),
        },
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert isinstance(request.user, User)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            answer = AnswerService.update_answer(
                user=request.user,
                answer_id=int(kwargs["pk"]),
                **serializer.validated_data,
            )
        except PermissionDenied as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        return Response(
            {
                "answer_id": answer.id,
                "updated_at": answer.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_200_OK,
        )

    # 답변 채택
    @extend_schema(
        tags=["Qna"],
        summary="답변 채택",
        responses={
            200: OpenApiResponse(description="채택 성공"),
            401: OpenApiResponse(description="로그인한 사용자만 답변을 채택할 수 있습니다."),
            403: OpenApiResponse(description="본인이 작성한 질문의 답변만 채택할 수 있습니다."),
            404: OpenApiResponse(description="해당 질문 또는 답변을 찾을 수 없습니다."),
            409: OpenApiResponse(description="이미 채택된 답변이 존재합니다."),
        },
    )
    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request: Request, pk: int | None = None) -> Response:
        assert isinstance(request.user, User)
        assert pk is not None
        try:
            answer = AnswerService.accept_answer(user=request.user, answer_id=int(pk))
        except PermissionDenied as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            error_msg = str(list(e.detail.values())[0]) if isinstance(e.detail, dict) else str(e.detail[0])
            return Response({"error_detail": error_msg}, status=status.HTTP_409_CONFLICT)
        return Response(
            {
                "question_id": answer.questions.id,
                "answer_id": answer.id,
                "is_adopted": True,
            },
            status=status.HTTP_200_OK,
        )

    # 답변 댓글 등록
    @extend_schema(
        tags=["Qna"],
        summary="답변 댓글 등록",
        request=CommentCreateSerializer,
        responses={
            201: OpenApiResponse(description="댓글 등록 성공"),
            400: OpenApiResponse(description="댓글 내용은 1~500자 사이로 입력해야 합니다."),
            401: OpenApiResponse(description="로그인한 사용자만 댓글을 작성할 수 있습니다."),
            403: OpenApiResponse(description="댓글 작성 권한이 없습니다."),
            404: OpenApiResponse(description="해당 답변을 찾을 수 없습니다."),
        },
    )
    @action(detail=True, methods=["post"], url_path="comments")
    def comment(self, request: Request, pk: int | None = None) -> Response:
        assert isinstance(request.user, User)
        assert pk is not None
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = AnswerService.create_comment(
            user=request.user,
            answer_id=int(pk),
            content=serializer.validated_data["content"],
        )
        return Response(
            {
                "comment_id": comment.id,
                "answer_id": int(pk),
                "author_id": request.user.id,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_201_CREATED,
        )


class AIAnswerViewSet(viewsets.GenericViewSet[Any]):
    permission_classes = [IsAuthenticated]

    # AI 답변 생성/조회
    @extend_schema(
        summary="AI 답변 생성/조회",
        responses={
            201: OpenApiResponse(description="AI 답변 생성/조회 성공"),
            401: OpenApiResponse(description="로그인한 사용자만 요청할 수 있습니다."),
            404: OpenApiResponse(description="질문 데이터를 찾을 수 없습니다."),
            409: OpenApiResponse(description="이미 AI가 답변을 생성했습니다."),
        },
    )
    def retrieve(self, request: Request, question_id: int | None = None) -> Response:
        assert question_id is not None
        try:
            ai_answer = AnswerService.get_or_create_ai_answer(int(question_id))
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            error_msg = str(list(e.detail.values())[0]) if isinstance(e.detail, dict) else str(e.detail[0])
            return Response({"error_detail": error_msg}, status=status.HTTP_409_CONFLICT)
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
