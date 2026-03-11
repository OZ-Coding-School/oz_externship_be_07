from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.exam.models.exam_submission_models import ExamSubmission
from apps.exam.serializers.exam_submission_serializers import (
    ExamSubmissionListSerializer,
    ExamSubmissionDetailSerializer,
)
from apps.exam.servieces.exam_submission_services import ExamSubmissionService


class ExamSubmissionListAPIView(APIView):
    @extend_schema(
        tags=["쪽지시험 응시 내역 관리"],
        summary="쪽지시험 응시 내역 목록 조회",
        parameters=[
            OpenApiParameter(name="page", type=int, description="페이지 번호"),
            OpenApiParameter(name="size", type=int, description="페이지당 개수"),
            OpenApiParameter(name="search_keyword", type=str, description="학생 이름 검색"),
        ],
        responses={200: ExamSubmissionListSerializer(many=True)},
    )
    def get(self, request):
        # Service에서 필터링된 쿼리셋 획득 (select_related 최적화 포함)
        queryset = ExamSubmissionService.get_submission_list(search_keyword=request.query_params.get("search_keyword"))

        serializer = ExamSubmissionListSerializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data}, status=status.HTTP_200_OK)


class ExamSubmissionDetailAPIView(APIView):
    @extend_schema(
        tags=["쪽지시험 응시 내역 관리"],
        summary="쪽지시험 응시 내역 상세 조회",
        responses={200: ExamSubmissionDetailSerializer, 404: "Not Found"},
    )
    def get(self, request, submission_id):
        # 상세 조회는 단일 객체이므로 직접 조회 혹은 Service 활용 가능
        submission = get_object_or_404(ExamSubmission, id=submission_id)
        serializer = ExamSubmissionDetailSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["쪽지시험 응시 내역 관리"],
        summary="쪽지시험 응시 내역 삭제",
        responses={
            200: {"example": {"submission_id": 123}},
            404: {"error_detail": "해당 응시 내역을 찾을 수 없습니다."},
            409: {"error_detail": "삭제 시 충돌이 발생했습니다."},
        },
    )
    def delete(self, request, submission_id):
        try:
            # Service를 통한 삭제 처리
            deleted_id = ExamSubmissionService.delete_submission(submission_id)
            return Response({"submission_id": deleted_id}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"error_detail": "응시 내역 삭제 처리 중 충돌이 발생했습니다."}, status=status.HTTP_409_CONFLICT
            )
