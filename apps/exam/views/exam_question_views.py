import json

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.exam.serializers.exam_deployment_serializers import ErrorDetailSerializer
from apps.exam.serializers.exam_question_serializers import (
    ExamQuestionCreateSerializer,
    ExamQuestionDeleteResponseSerializer,
    ExamQuestionResponseSerializer,
    ExamQuestionUpdateSerializer,
    serialize_question_response,
)


class ExamQuestionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 문제 목록 조회",
        responses={200: ExamQuestionResponseSerializer(many=True), 404: ErrorDetailSerializer},
    )
    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, pk=exam_id)
        questions = ExamQuestion.objects.filter(exam=exam).order_by("id")
        results = [serialize_question_response(q) for q in questions]
        return Response(results, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 문제 등록",
        request=ExamQuestionCreateSerializer,
        responses={
            201: ExamQuestionResponseSerializer,
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
    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)

        serializer = ExamQuestionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": "요청 값이 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        options_json = None
        if data.get("options") is not None:
            options_json = json.dumps(data["options"], ensure_ascii=False)

        question = ExamQuestion.objects.create(
            exam=exam,
            type=data["type"],
            question=data["question"],
            prompt=data.get("prompt"),
            options_json=options_json,
            blank_count=data.get("blank_count"),
            answer=data["correct_answer"],
            point=data["point"],
            explanation=data["explanation"],
        )

        return Response(serialize_question_response(question), status=status.HTTP_201_CREATED)


class ExamQuestionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 문제 상세 조회",
        responses={200: ExamQuestionResponseSerializer, 404: ErrorDetailSerializer},
    )
    def get(self, request, question_id):
        question = get_object_or_404(ExamQuestion, id=question_id)
        return Response(serialize_question_response(question), status=status.HTTP_200_OK)

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 문제 수정",
        request=ExamQuestionUpdateSerializer,
        responses={
            200: OpenApiResponse(response=ExamQuestionResponseSerializer, description="OK"),
            400: OpenApiResponse(
                response=ErrorDetailSerializer,
                description="Bad Request",
                examples=[OpenApiExample("400", value={"error_detail": "유효하지 않은 문제 수정 데이터입니다."})],
            ),
            401: OpenApiResponse(
                response=ErrorDetailSerializer,
                description="Unauthorized",
                examples=[OpenApiExample("401", value={"error_detail": "자격 인증 데이터가 제공되이 않았습니다."})],
            ),
            403: OpenApiResponse(
                response=ErrorDetailSerializer,
                description="Forbidden",
                examples=[OpenApiExample("403", value={"error_detail": "쪽지시험 문제 수정 권한이 없습니다."})],
            ),
            404: OpenApiResponse(
                response=ErrorDetailSerializer,
                description="Not Found",
                examples=[OpenApiExample("404", value={"error_detail": "수정하려는 문제 정보를 찾을 수 없습니다."})],
            ),
            409: OpenApiResponse(
                response=ErrorDetailSerializer,
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "409",
                        value={"error_detail": "시험 문제 수 제한 또는 총 배점을 초과하여 문제를 수정할 수 없습니다."},
                    )
                ],
            ),
        },
    )
    def patch(self, request, question_id):
        question = get_object_or_404(ExamQuestion, id=question_id)

        serializer = ExamQuestionUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": "요청 값이 올바르지 않음."}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if "options" in data:
            question.options_json = (
                json.dumps(data["options"], ensure_ascii=False) if data["options"] is not None else None
            )
        if "type" in data:
            question.type = data["type"]
        if "question" in data:
            question.question = data["question"]
        if "prompt" in data:
            question.prompt = data["prompt"]
        if "blank_count" in data:
            question.blank_count = data["blank_count"]
        if "correct_answer" in data:
            question.answer = data["correct_answer"]
        if "point" in data:
            question.point = data["point"]
        if "explanation" in data:
            question.explanation = data["explanation"]

        question.save()

        return Response(serialize_question_response(question), status=status.HTTP_200_OK)

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
    def delete(self, request, question_id):
        question = get_object_or_404(ExamQuestion, id=question_id)
        exam_id = question.exam_id
        question.delete()
        return Response(
            {"exam_id": exam_id, "question_id": question_id},
            status=status.HTTP_200_OK,
        )
