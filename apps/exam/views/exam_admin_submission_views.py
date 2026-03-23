from typing import Any

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.exam.core.error_base import ExamBaseAPIView
from apps.exam.core.permissions import IsStaffUser
from apps.exam.serializers.exam_submission_serializers import (
    ExamSubmissionDetailSerializer,
    ExamSubmissionListSerializer,
)
from apps.exam.services.exam_admin_submission_services import ExamAdminSubmissionService


class ExamAdminSubmissionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"
    page_query_param = "page"
    max_page_size = 100

    def get_paginated_response(self, data: Any) -> Response:
        return Response(
            {
                "count": self.page.paginator.count if self.page else 0,
                "previous": self.get_previous_link(),
                "next": self.get_next_link(),
                "results": data,
            }
        )


class ExamAdminSubmissionListAPIView(ExamBaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser]
    permission_error_msgs = {"GET": "쪽지시험 응시 내역 조회 권한이 없습니다."}
    validation_error_msgs = {"GET": "유효하지 않은 조회 요청입니다."}

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 응시 내역 목록 조회",
        description="관리자용 쪽지시험 응시 내역 목록을 페이지네이션하여 반환합니다.",
        parameters=[
            OpenApiParameter(name="page", description="페이지 번호", type=int),
            OpenApiParameter(name="size", description="페이지당 아이템 개수", type=int),
            OpenApiParameter(name="search_keyword", description="수강생 이름/닉네임 검색어", type=str),
            OpenApiParameter(name="cohort_id", description="기수 ID 필터", type=int),
            OpenApiParameter(name="exam_id", description="시험 ID 필터", type=int),
            OpenApiParameter(name="sort", description="정렬 필드 (score, started_at, finished_at)", type=str),
            OpenApiParameter(name="order", description="정렬 순서 (asc, desc)", type=str),
        ],
        responses={
            200: ExamSubmissionListSerializer(many=True),
            400: OpenApiResponse(description="유효하지 않은 조회 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="쪽지시험 응시 내역 조회 권한이 없습니다."),
            404: OpenApiResponse(description="조회된 응시 내역이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        queryset = ExamAdminSubmissionService.get_submission_queryset(request.query_params.dict())

        if not queryset.exists():
            raise NotFound("조회된 응시 내역이 없습니다.")

        paginator = ExamAdminSubmissionPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ExamSubmissionListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ExamSubmissionListSerializer(queryset, many=True)
        return Response(
            {
                "count": len(serializer.data),
                "previous": None,
                "next": None,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ExamAdminSubmissionDetailAPIView(ExamBaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser]
    permission_error_msgs = {
        "GET": "쪽지시험 응시 상세 조회 권한이 없습니다.",
        "DELETE": "쪽지시험 응시 내역 삭제 권한이 없습니다.",
    }
    validation_error_msgs = {
        "GET": "유효하지 않은 상세 조회 요청입니다.",
        "DELETE": "유효하지 않은 응시 내역 삭제 요청입니다.",
    }

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 응시 내역 상세 조회",
        description="특정 응시 내역의 상세 정보와 채점 결과를 조회합니다.",
        responses={
            200: ExamSubmissionDetailSerializer,
            400: OpenApiResponse(description="유효하지 않은 상세 조회 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="쪽지시험 응시 상세 조회 권한이 없습니다."),
            404: OpenApiResponse(description="해당 응시 내역을 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, submission_id: int) -> Response:
        submission = ExamAdminSubmissionService.get_submission_detail(submission_id)
        serializer = ExamSubmissionDetailSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 응시 내역 삭제",
        description="특정 응시 내역을 삭제합니다.",
        responses={
            200: OpenApiResponse(description="삭제된 submission_id 반환"),
            400: OpenApiResponse(description="유효하지 않은 응시 내역 삭제 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="쪽지시험 응시 내역 삭제 권한이 없습니다."),
            404: OpenApiResponse(description="삭제할 응시 내역을 찾을 수 없습니다."),
            409: OpenApiResponse(description="응시 내역 삭제 처리 중 충돌이 발생했습니다."),
        },
    )
    def delete(self, request: Request, submission_id: int) -> Response:
        deleted_id = ExamAdminSubmissionService.delete_submission(submission_id)
        return Response({"submission_id": deleted_id}, status=status.HTTP_200_OK)
