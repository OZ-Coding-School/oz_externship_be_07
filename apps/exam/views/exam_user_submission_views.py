from typing import cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.permissions import STAFF_ROLES
from apps.exam.core.error_base import ExamBaseAPIView
from apps.exam.serializers.exam_submission_serializers import (
    ExamSubmissionCreateResponseSerializer,
    ExamSubmissionCreateSerializer,
    ExamSubmissionResultSerializer,
)
from apps.exam.services.exam_user_submission_services import ExamUserSubmissionService
from apps.users.models.models import User


class ExamSubmissionAPIView(ExamBaseAPIView):
    permission_classes = [IsAuthenticated]
    permission_error_msgs = {"POST": "권한이 없습니다."}
    validation_error_msgs = {"POST": "유효하지 않은 시험 응시 세션입니다."}

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 제출 API",
        description="시험 응시를 완료하고 답안을 제출합니다. 제출 시 자동 채점이 이루어집니다.",
        request=ExamSubmissionCreateSerializer,
        responses={
            201: ExamSubmissionCreateResponseSerializer,
            400: OpenApiResponse(description="유효하지 않은 시험 응시 세션입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 시험 정보를 찾을 수 없습니다."),
            409: OpenApiResponse(description="이미 제출된 시험입니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ExamSubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission = ExamUserSubmissionService.create_submission(
            user=cast(User, request.user), data=serializer.validated_data
        )

        response_serializer = ExamSubmissionCreateResponseSerializer(submission)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ExamSubmissionDetailAPIView(ExamBaseAPIView):
    permission_classes = [IsAuthenticated]
    permission_error_msgs = {"GET": "권한이 없습니다."}
    validation_error_msgs = {"GET": "유효하지 않은 시험 응시 세션입니다."}

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 결과 확인 API",
        description="특정 제출 건에 대한 상세 결과와 채점 내역을 조회합니다.",
        responses={
            200: ExamSubmissionResultSerializer,  # 명세서 구조 반영
            400: OpenApiResponse(description="유효하지 않은 시험 응시 세션입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 시험 정보를 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, submission_id: int) -> Response:
        submission = ExamUserSubmissionService.get_submission_detail(submission_id)

        is_staff = getattr(request.user, "role", None) in STAFF_ROLES
        if not is_staff and submission.submitter != request.user:
            raise PermissionDenied("권한이 없습니다.")

        serializer = ExamSubmissionResultSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)
