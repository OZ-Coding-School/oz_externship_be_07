from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.exam.serializers.admin_deployment_command_serializers import (
    ExamDeploymentCreateResponseSerializer,
    ExamDeploymentCreateSerializer,
    ExamDeploymentDeleteResponseSerializer,
    ExamDeploymentStatusUpdateResponseSerializer,
    ExamDeploymentStatusUpdateSerializer,
    ExamDeploymentUpdateResponseSerializer,
    ExamDeploymentUpdateSerializer,
)
from apps.exam.serializers.admin_deployment_query_serializers import (
    ExamDeploymentDetailSerializer,
    ExamDeploymentListResponseSerializer,
)
from apps.exam.views.exam_admin_deployment_command_views import (
    AdminExamDeploymentCreateAPIView,
    AdminExamDeploymentDeleteAPIView,
    AdminExamDeploymentStatusUpdateAPIView,
    AdminExamDeploymentUpdateAPIView,
)
from apps.exam.views.exam_admin_deployment_permissions import (
    CanCreateExamDeployment,
    CanDeleteExamDeployment,
    CanDetailExamDeployment,
    CanListExamDeployment,
    CanUpdateExamDeployment,
    CanUpdateExamDeploymentStatus,
)
from apps.exam.views.exam_admin_deployment_query_views import (
    AdminExamDeploymentDetailAPIView,
    AdminExamDeploymentListAPIView,
)
from apps.subject.core.error_base import SubjectBaseAPIView
from apps.subject.core.error_responses import ErrorResponseSerializer


class AdminExamDeploymentListCreateAPIView(SubjectBaseAPIView):
    def get_permissions(self) -> list[IsAuthenticated | CanCreateExamDeployment | CanListExamDeployment]:
        if self.request.method == "POST":
            return [IsAuthenticated(), CanCreateExamDeployment()]
        return [IsAuthenticated(), CanListExamDeployment()]

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 배포 목록 조회 API",
        responses={
            200: ExamDeploymentListResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        view = AdminExamDeploymentListAPIView.as_view()
        return view(request._request, *args, **kwargs)

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 배포 생성 API",
        request=ExamDeploymentCreateSerializer,
        responses={
            201: ExamDeploymentCreateResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            409: ErrorResponseSerializer,
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        view = AdminExamDeploymentCreateAPIView.as_view()
        return view(request._request, *args, **kwargs)


class AdminExamDeploymentDetailUpdateDeleteAPIView(SubjectBaseAPIView):
    def get_permissions(
        self,
    ) -> list[IsAuthenticated | CanDetailExamDeployment | CanUpdateExamDeployment | CanDeleteExamDeployment]:
        if self.request.method == "GET":
            return [IsAuthenticated(), CanDetailExamDeployment()]
        if self.request.method == "PATCH":
            return [IsAuthenticated(), CanUpdateExamDeployment()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), CanDeleteExamDeployment()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 배포 상세 조회 API",
        responses={
            200: ExamDeploymentDetailSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        view = AdminExamDeploymentDetailAPIView.as_view()
        return view(request._request, *args, **kwargs)

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 배포 정보 수정 API",
        request=ExamDeploymentUpdateSerializer,
        responses={
            200: ExamDeploymentUpdateResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        view = AdminExamDeploymentUpdateAPIView.as_view()
        return view(request._request, *args, **kwargs)

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 배포 삭제 API",
        responses={
            200: ExamDeploymentDeleteResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            409: ErrorResponseSerializer,
        },
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        view = AdminExamDeploymentDeleteAPIView.as_view()
        return view(request._request, *args, **kwargs)


class AdminExamDeploymentStatusAPIView(SubjectBaseAPIView):
    def get_permissions(self) -> list[IsAuthenticated | CanUpdateExamDeploymentStatus]:
        return [IsAuthenticated(), CanUpdateExamDeploymentStatus()]

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 배포 on/off API",
        request=ExamDeploymentStatusUpdateSerializer,
        responses={
            200: ExamDeploymentStatusUpdateResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            409: ErrorResponseSerializer,
        },
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        view = AdminExamDeploymentStatusUpdateAPIView.as_view()
        return view(request._request, *args, **kwargs)
