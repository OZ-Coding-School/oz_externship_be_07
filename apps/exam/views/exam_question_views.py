from typing import Any, Type, cast

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import exceptions, mixins, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.exam.core.error_base import ExamBaseViewSet
from apps.exam.core.permissions import IsAdmin
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.exam.serializers.exam_question_serializers import (
    ErrorDetailSerializer,
    ExamQuestionCreateResponseSerializer,
    ExamQuestionCreateSerializer,
    ExamQuestionDeleteResponseSerializer,
    ExamQuestionUpdateResponseSerializer,
    ExamQuestionUpdateSerializer,
)
from apps.exam.services.exam_question_services import ExamQuestionService


class ExamQuestionViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, ExamBaseViewSet):

    permission_classes = [IsAdmin]
    queryset = ExamQuestion.objects.all()
    lookup_field = "id"

    def get_serializer_class(self) -> Type[Serializer[Any]]:
        if self.action == "create":
            return ExamQuestionCreateSerializer
        if self.action == "update":
            return ExamQuestionUpdateSerializer
        return ExamQuestionCreateSerializer

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 문제 등록",
        request=ExamQuestionCreateSerializer,
        responses={
            201: ExamQuestionCreateResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
            409: ErrorDetailSerializer,
        },
        examples=[
            OpenApiExample(
                "400",
                value={"error_detail": "유효하지 않은 문제 등록 데이터입니다."},
                status_codes=["400"],
                response_only=True,
            ),
            OpenApiExample(
                "401",
                value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                status_codes=["401"],
                response_only=True,
            ),
            OpenApiExample(
                "403",
                value={"error_detail": "쪽지시험 문제 등록 권한이 없습니다."},
                status_codes=["403"],
                response_only=True,
            ),
            OpenApiExample(
                "404",
                value={"error_detail": "해당 쪽지시험 정보를 찾을 수 없습니다."},
                status_codes=["404"],
                response_only=True,
            ),
            OpenApiExample(
                "409",
                value={"error_detail": "해당 쪽지시험에 등록 가능한 문제 수 또는 총 배점을 초과했습니다."},
                status_codes=["409"],
                response_only=True,
            ),
        ],
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exam_id = cast(int, self.kwargs.get("exam_id"))
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise exceptions.NotFound("해당 쪽지시험 정보를 찾을 수 없습니다.")

        question = ExamQuestionService.create_question(exam, serializer.validated_data)
        response_serializer = ExamQuestionCreateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 문제 수정",
        request=ExamQuestionUpdateSerializer,
        responses={
            200: ExamQuestionUpdateResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
            409: ErrorDetailSerializer,
        },
        examples=[
            OpenApiExample(
                "400",
                value={"error_detail": "유효하지 않은 문제 수정 데이터입니다."},
                status_codes=["400"],
                response_only=True,
            ),
            OpenApiExample(
                "401",
                value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                status_codes=["401"],
                response_only=True,
            ),
            OpenApiExample(
                "403",
                value={"error_detail": "쪽지시험 문제 수정 권한이 없습니다."},
                status_codes=["403"],
                response_only=True,
            ),
            OpenApiExample(
                "404",
                value={"error_detail": "수정하려는 문제 정보를 찾을 수 없습니다."},
                status_codes=["404"],
                response_only=True,
            ),
            OpenApiExample(
                "409",
                value={"error_detail": "시험 문제 수 제한 또는 총 배점을 초과하여 문제를 수정할 수 없습니다."},
                status_codes=["409"],
                response_only=True,
            ),
        ],
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            instance = ExamQuestion.objects.get(id=cast(int, self.kwargs.get("id")))
        except ExamQuestion.DoesNotExist:
            raise exceptions.NotFound("수정하려는 문제 정보를 찾을 수 없습니다.")

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_question = ExamQuestionService.update_question(instance, serializer.validated_data)
        response_serializer = ExamQuestionUpdateResponseSerializer(updated_question)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 문제 삭제",
        responses={
            200: ExamQuestionDeleteResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
            409: ErrorDetailSerializer,
        },
        examples=[
            OpenApiExample(
                "400",
                value={"error_detail": "유효하지 않은 문제 삭제 요청입니다."},
                status_codes=["400"],
                response_only=True,
            ),
            OpenApiExample(
                "401",
                value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                status_codes=["401"],
                response_only=True,
            ),
            OpenApiExample(
                "403",
                value={"error_detail": "쪽지시험 문제 삭제 권한이 없습니다."},
                status_codes=["403"],
                response_only=True,
            ),
            OpenApiExample(
                "404",
                value={"error_detail": "삭제할 문제 정보를 찾을 수 없습니다."},
                status_codes=["404"],
                response_only=True,
            ),
            OpenApiExample(
                "409",
                value={"error_detail": "쪽지시험 문제 삭제 처리 중 충돌이 발생했습니다."},
                status_codes=["409"],
                response_only=True,
            ),
        ],
    )
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            question = ExamQuestion.objects.get(id=cast(int, self.kwargs.get("id")))
        except ExamQuestion.DoesNotExist:
            raise exceptions.NotFound("삭제할 문제 정보를 찾을 수 없습니다.")

        result = ExamQuestionService.delete_question(question)
        return Response(result, status=status.HTTP_200_OK)
