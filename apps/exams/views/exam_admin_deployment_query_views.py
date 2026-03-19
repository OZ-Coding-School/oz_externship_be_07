from typing import Any
from urllib.parse import urlencode

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.serializers.admin_deployment_query_serializers import (
    ExamDeploymentDetailSerializer,
    ExamDeploymentListQuerySerializer,
    ExamDeploymentListResponseSerializer,
)
from apps.exam.services.exam_admin_deployment_services import ExamDeploymentService
from apps.exam.views.exam_admin_deployment_permissions import (
    CanDetailExamDeployment,
    CanListExamDeployment,
)
from apps.subject.core.error_base import SubjectBaseAPIView
from apps.subject.core.error_responses import ErrorResponseSerializer


def error_response(*, message: str, http_status: int) -> Response:
    return Response({"error_detail": message}, status=http_status)


class AdminExamDeploymentQueryBaseAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated]

    ORDERING_MAP = {
        "created_at": "created_at",
        "submit_count": "submit_count",
        "avg_score": "avg_score",
    }

    def _get_deployment(self, deployment_id: int) -> ExamDeployment | None:
        return ExamDeploymentService.get_detail_queryset().filter(id=deployment_id).first()

    def _build_page_url(self, request: Request, page: int, page_size: int) -> str:
        params = request.query_params.copy()
        params["page"] = str(page)
        params["page_size"] = str(page_size)
        return f"{request.build_absolute_uri(request.path)}?{urlencode(params, doseq=True)}"

    def _build_list_item(self, deployment: ExamDeployment) -> dict[str, Any]:
        subject = deployment.exam.subject
        cohort = deployment.cohort
        course = cohort.course

        raw_avg_score = getattr(deployment, "avg_score", 0.0)
        if raw_avg_score is None:
            raw_avg_score = 0.0

        return {
            "id": deployment.id,
            "submit_count": getattr(deployment, "submit_count", 0),
            "avg_score": round(float(raw_avg_score), 1),
            "status": ExamDeploymentService.format_list_status(deployment.status),
            "exam": {
                "id": deployment.exam.id,
                "title": deployment.exam.title,
                "thumbnail_img_url": deployment.exam.thumbnail_img_url,
            },
            "subject": {
                "id": subject.id,
                "name": subject.title,
            },
            "cohort": {
                "id": cohort.id,
                "number": cohort.number,
                "display": f"{course.name} {cohort.number}기",
                "course": {
                    "id": course.id,
                    "name": course.name,
                    "tag": course.tag,
                },
            },
            "created_at": ExamDeploymentService.format_datetime(deployment.created_at),
        }

    def _build_detail_response(self, deployment: ExamDeployment) -> dict[str, Any]:
        submit_count = ExamDeploymentService.get_submit_count(deployment.id)
        total_student_count = ExamDeploymentService.get_total_student_count(deployment.cohort_id)
        not_submitted_count = max(total_student_count - submit_count, 0)

        subject = deployment.exam.subject
        cohort = deployment.cohort
        course = cohort.course

        return {
            "id": deployment.id,
            "exam_access_url": ExamDeploymentService.build_exam_access_url(deployment.id),
            "access_code": deployment.access_code,
            "cohort": {
                "id": cohort.id,
                "number": cohort.number,
                "display": f"{course.name} {cohort.number}기",
                "course": {
                    "id": course.id,
                    "name": course.name,
                    "tag": course.tag,
                },
            },
            "submit_count": submit_count,
            "not_submitted_count": not_submitted_count,
            "duration_time": deployment.duration_time,
            "open_at": ExamDeploymentService.format_datetime(deployment.open_at),
            "close_at": ExamDeploymentService.format_datetime(deployment.close_at),
            "created_at": ExamDeploymentService.format_datetime(deployment.created_at),
            "exam": {
                "id": deployment.exam.id,
                "title": deployment.exam.title,
                "thumbnail_img_url": deployment.exam.thumbnail_img_url,
            },
            "subject": {
                "id": subject.id,
                "name": subject.title,
            },
        }


class AdminExamDeploymentListAPIView(AdminExamDeploymentQueryBaseAPIView):
    permission_classes = [IsAuthenticated, CanListExamDeployment]

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 배포 목록 조회 API",
        responses={
            200: ExamDeploymentListResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = ExamDeploymentListQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return error_response(
                message="유효하지 않은 조회 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        params = serializer.validated_data
        queryset = ExamDeploymentService.get_list_queryset()

        search_keyword = params.get("search_keyword")
        subject_id = params.get("subject_id")
        cohort_id = params.get("cohort_id")
        sort = params.get("sort", "created_at")
        order = params.get("order", "desc")
        page = params.get("page", 1)
        page_size = params.get("page_size", 10)

        if search_keyword:
            queryset = queryset.filter(exam__title__icontains=search_keyword)

        if subject_id:
            queryset = queryset.filter(exam__subject_id=subject_id)

        if cohort_id:
            queryset = queryset.filter(cohort_id=cohort_id)

        sort_field = self.ORDERING_MAP.get(sort)
        if sort_field is None:
            return error_response(
                message="유효하지 않은 조회 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        ordering = f"-{sort_field}" if order == "desc" else sort_field
        secondary_ordering = "-id" if order == "desc" else "id"
        queryset = queryset.order_by(ordering, secondary_ordering)

        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = list(queryset[start:end])

        response_data = {
            "count": total_count,
            "previous": self._build_page_url(request, page - 1, page_size) if page > 1 else None,
            "next": self._build_page_url(request, page + 1, page_size) if end < total_count else None,
            "results": [self._build_list_item(item) for item in items],
        }
        return Response(response_data, status=status.HTTP_200_OK)


class AdminExamDeploymentDetailAPIView(AdminExamDeploymentQueryBaseAPIView):
    permission_classes = [IsAuthenticated, CanDetailExamDeployment]

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 배포 상세 조회 API",
        responses={
            200: ExamDeploymentDetailSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, deployment_id: int, *args: Any, **kwargs: Any) -> Response:
        deployment = self._get_deployment(deployment_id)
        if deployment is None:
            return error_response(
                message="해당 배포 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        return Response(self._build_detail_response(deployment), status=status.HTTP_200_OK)
