from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subject.serializers.cohort_serializers import (
    CohortAvgScoreItemSerializer,
    CohortStudentItemSerializer,
    ErrorDetailStringSerializer,
)
from apps.subject.services.cohort_services import CohortService
from apps.subject.views.cohort_views import check_admin_role, error_response


class AdminCourseCohortAvgScoresAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["subjects"],
        summary="어드민 기수별 평균 점수 조회 API",
        responses={
            200: OpenApiResponse(response=CohortAvgScoreItemSerializer(many=True), description="OK"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
            404: OpenApiResponse(response=ErrorDetailStringSerializer, description="Not Found"),
        },
    )
    def get(self, request: Request, course_id: int) -> Response:
        permission_error = check_admin_role(request)
        if permission_error:
            return permission_error

        try:
            result = CohortService.get_cohort_avg_scores(course_id=course_id)
        except Http404:
            return error_response(
                message="과정을 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)


class AdminCohortStudentListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["subjects"],
        summary="어드민 기수별 수강생 목록 조회 API",
        responses={
            200: OpenApiResponse(response=CohortStudentItemSerializer(many=True), description="OK"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
            404: OpenApiResponse(response=ErrorDetailStringSerializer, description="Not Found"),
        },
    )
    def get(self, request: Request, cohort_id: int) -> Response:
        permission_error = check_admin_role(request)
        if permission_error:
            return permission_error

        try:
            cohort_students = CohortService.get_cohort_students(cohort_id=cohort_id)
        except Http404:
            return error_response(
                message="기수를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        data = [
            {
                "value": cohort_student.user.nickname,
                "label": cohort_student.user.name,
            }
            for cohort_student in cohort_students
        ]
        return Response(data, status=status.HTTP_200_OK)
