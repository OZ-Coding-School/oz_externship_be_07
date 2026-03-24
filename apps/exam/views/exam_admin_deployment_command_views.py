from typing import Any

from django.db import DatabaseError, IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.exam.core.exceptions import AdminDeploymentDuplicateError
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.serializers.admin_deployment_command_serializers import (
    ExamDeploymentCreateResponseSerializer,
    ExamDeploymentCreateSerializer,
    ExamDeploymentDeleteResponseSerializer,
    ExamDeploymentStatusUpdateResponseSerializer,
    ExamDeploymentStatusUpdateSerializer,
    ExamDeploymentUpdateResponseSerializer,
    ExamDeploymentUpdateSerializer,
)
from apps.exam.services.exam_admin_deployment_services import ExamDeploymentService
from apps.exam.views.exam_admin_deployment_permissions import (
    CanCreateExamDeployment,
    CanDeleteExamDeployment,
    CanUpdateExamDeployment,
    CanUpdateExamDeploymentStatus,
)
from apps.subject.core.error_base import SubjectBaseAPIView
from apps.subject.core.error_responses import ErrorResponseSerializer
from apps.subject.models.cohort_models import Cohort


def error_response(*, message: str, http_status: int) -> Response:
    return Response({"error_detail": message}, status=http_status)


class AdminExamDeploymentCommandBaseAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated]

    def _get_deployment(self, deployment_id: int) -> ExamDeployment | None:
        return ExamDeploymentService.get_detail_queryset().filter(id=deployment_id).first()


class AdminExamDeploymentCreateAPIView(AdminExamDeploymentCommandBaseAPIView):
    permission_classes = [IsAuthenticated, CanCreateExamDeployment]

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
        serializer = ExamDeploymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="유효하지 않은 배포 생성 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = dict(serializer.validated_data)
        exam_id = validated_data.pop("exam_id")
        cohort_id = validated_data.pop("cohort_id")

        exam = Exam.objects.filter(id=exam_id).first()
        cohort = Cohort.objects.filter(id=cohort_id).first()

        if exam is None or cohort is None:
            return error_response(
                message="배포 대상 과정-기수 또는 시험 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        validated_data["exam"] = exam
        validated_data["cohort"] = cohort

        try:
            deployment = ExamDeploymentService.create_deployment(validated_data)
        except AdminDeploymentDuplicateError:
            return error_response(
                message="동일한 조건의 배포가 이미 존재합니다.",
                http_status=status.HTTP_409_CONFLICT,
            )
        except IntegrityError:
            return error_response(
                message="유효하지 않은 배포 생성 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        except DatabaseError:
            return error_response(
                message="유효하지 않은 배포 생성 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"pk": deployment.id}, status=status.HTTP_201_CREATED)


class AdminExamDeploymentUpdateAPIView(AdminExamDeploymentCommandBaseAPIView):
    permission_classes = [IsAuthenticated, CanUpdateExamDeployment]

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
    def patch(self, request: Request, deployment_id: int, *args: Any, **kwargs: Any) -> Response:
        deployment = self._get_deployment(deployment_id)
        if deployment is None:
            return error_response(
                message="수정할 배포 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ExamDeploymentUpdateSerializer(instance=deployment, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                message="유효하지 않은 배포 수정 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        updated_deployment = ExamDeploymentService.update_deployment(deployment, serializer.validated_data)

        response_data = {
            "deployment_id": updated_deployment.id,
            "duration_time": updated_deployment.duration_time,
            "open_at": ExamDeploymentService.format_datetime(updated_deployment.open_at),
            "close_at": ExamDeploymentService.format_datetime(updated_deployment.close_at),
            "updated_at": ExamDeploymentService.format_datetime(updated_deployment.updated_at),
        }
        return Response(response_data, status=status.HTTP_200_OK)


class AdminExamDeploymentStatusUpdateAPIView(AdminExamDeploymentCommandBaseAPIView):
    permission_classes = [IsAuthenticated, CanUpdateExamDeploymentStatus]

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
    def patch(self, request: Request, deployment_id: int, *args: Any, **kwargs: Any) -> Response:
        deployment = self._get_deployment(deployment_id)
        if deployment is None:
            return error_response(
                message="해당 배포 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ExamDeploymentStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="유효하지 않은 배포 상태 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_deployment = ExamDeploymentService.update_status(
                deployment,
                serializer.validated_data["status"],
            )
        except IntegrityError:
            return error_response(
                message="배포 상태 변경 중 충돌이 발생했습니다.",
                http_status=status.HTTP_409_CONFLICT,
            )
        except DatabaseError:
            return error_response(
                message="유효하지 않은 배포 상태 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = {
            "deployment_id": updated_deployment.id,
            "status": ExamDeploymentService.format_status_response(updated_deployment.status),
        }
        return Response(response_data, status=status.HTTP_200_OK)


class AdminExamDeploymentDeleteAPIView(AdminExamDeploymentCommandBaseAPIView):
    permission_classes = [IsAuthenticated, CanDeleteExamDeployment]

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
    def delete(self, request: Request, deployment_id: int, *args: Any, **kwargs: Any) -> Response:
        deployment = self._get_deployment(deployment_id)
        if deployment is None:
            return error_response(
                message="삭제할 배포 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        try:
            deleted_id = ExamDeploymentService.delete_deployment(deployment)
        except IntegrityError:
            return error_response(
                message="배포 삭제 처리 중 충돌이 발생했습니다.",
                http_status=status.HTTP_409_CONFLICT,
            )
        except DatabaseError:
            return error_response(
                message="유효하지 않은 배포 삭제 요청입니다.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"deployment_id": deleted_id}, status=status.HTTP_200_OK)
