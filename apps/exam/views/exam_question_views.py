from typing import Any

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import exceptions, parsers, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.exam.core.error_base import ExamBaseAPIView
from apps.exam.core.permissions import IsStaffUser
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


class ExamQuestionCreateAPIView(ExamBaseAPIView):

    permission_classes = [IsStaffUser, IsAuthenticated]

    @extend_schema(
        tags=["Admin_exams"],
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
    def post(self, request: Request, exam_id: int, *args: Any, **kwargs: Any) -> Response:

        serializer = ExamQuestionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise NotFound("해당 쪽지시험 정보를 찾을 수 없습니다.")

        question = ExamQuestionService.create_question(exam, serializer.validated_data)
        response_serializer = ExamQuestionCreateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ExamQuestionUpdateDeleteAPIView(ExamBaseAPIView):
    permission_classes = [IsStaffUser, IsAuthenticated]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    @extend_schema(
        tags=["Admin_exams"],
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
    def put(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:

        serializer = ExamQuestionUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = ExamQuestion.objects.get(id=question_id)
        except ExamQuestion.DoesNotExist:
            raise NotFound("수정하려는 문제 정보를 찾을 수 없습니다.")

        updated_question = ExamQuestionService.update_question(question, serializer.validated_data)
        response_serializer = ExamQuestionUpdateResponseSerializer(updated_question)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Admin_exams"],
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
    def delete(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:

        try:
            question = ExamQuestion.objects.get(id=question_id)
        except ExamQuestion.DoesNotExist:
            raise exceptions.NotFound("삭제할 문제 정보를 찾을 수 없습니다.")

        result = ExamQuestionService.delete_question(question)
        response_serializer = ExamQuestionDeleteResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
