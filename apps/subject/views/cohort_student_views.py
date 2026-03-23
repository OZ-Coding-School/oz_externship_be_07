from django.core.paginator import Paginator
from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subject.serializers.cohort_student_serializers import (
    StudentListItemSerializer,
    StudentListQuerySerializer,
    StudentSubjectScoreItemSerializer,
)
from apps.subject.services.cohort_student_services import CohortStudentService


# 1. 수강생 목록 조회
class StudentListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["subjects"],
        summary="어드민 수강생 목록 조회",
        description="검색, 상태 필터를 통해 수강생 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(name="page", type=int, required=False),
            OpenApiParameter(name="page_size", type=int, required=False),
            OpenApiParameter(name="search", type=str, required=False),
            OpenApiParameter(
                name="status",
                type=str,
                required=False,
                enum=["activated", "deactivated", "withdrew"],
            ),
        ],
        responses={200: StudentListItemSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        query_serializer = StudentListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        data = query_serializer.validated_data

        queryset = CohortStudentService.get_student_list(
            page=data.get("page", 1),
            page_size=data.get("page_size", 10),
            search=data.get("search"),
            status=data.get("status"),
        )

        paginator = Paginator(queryset, data.get("page_size", 10))
        page_obj = paginator.get_page(data.get("page", 1))

        serializer = StudentListItemSerializer(page_obj.object_list, many=True)

        return Response(
            {
                "count": paginator.count,
                "next": None,
                "previous": None,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# 2. 학생별 점수 조회
class StudentScoreAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["subjects"],
        summary="학생별 과목 점수 조회",
        description="특정 학생의 과목별 점수를 조회합니다.",
        responses={200: StudentSubjectScoreItemSerializer(many=True)},
    )
    def get(self, request: Request, student_id: int) -> Response:
        try:
            data = CohortStudentService.get_student_scores(student_id=student_id)
        except Http404:
            return Response(
                {"error_detail": "학생을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StudentSubjectScoreItemSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
