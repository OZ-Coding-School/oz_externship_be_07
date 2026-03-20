from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_with_status_code, get_object_or_404

from apps.exam.models.exam_submission_models import ExamSubmission
from apps.exam.serializers.exam_submission_serializers import (
    ExamSubmissionCreateSerializer,
    ExamSubmissionResultSerializer,
    ExamSubmissionCreateResponseSerializer
)

from apps.exam.services.exam_user_submission_services import ExamSubmissionService


class ExamSubmissionAPIView(APIView):
    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 제출",
        description="사용자가 작성한 답안을 제출하고 채점 결과를 반환합니다.",
        request=ExamSubmissionCreateSerializer,
        responses={201: ExamSubmissionCreateResponseSerializer}
    )
    def post(self, request):
        serializer = ExamSubmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            submission = ExamSubmissionService.create_submission(
                user=request.user,
                data=serializer.validated_data
            )

            response_serializer = ExamSubmissionCreateResponseSerializer(submission)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamSubmissionDetailAPIView(APIView):
    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 결과 상세 조회",
        description="특정 제출 건에 대한 상세 결과 및 채점 내역을 조회합니다.",
        responses={200: ExamSubmissionResultSerializer}
    )
    def get(self, request, submission_id):
        submission = ExamSubmissionService.get_submission_detail(submission_id)

        serializer = ExamSubmissionResultSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)