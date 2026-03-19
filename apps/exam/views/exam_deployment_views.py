from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.exam.serializers.deployment_serializers import (
    DeploymentDetailResponseSerializer,
    DeploymentListQuerySerializer,
    DeploymentListResponseSerializer,
    DeploymentStatusResponseSerializer,
)
from apps.exam.services.exam_deployment_access_services import (
    ExamDeploymentAccessService,
)
from apps.exam.services.exam_deployment_services import (
    DeploymentForbiddenError,
    DeploymentGoneError,
    DeploymentInvalidSessionError,
    DeploymentNotFoundError,
    ExamDeploymentService,
    UserNotFoundError,
)
from apps.subject.core.error_base import SubjectBaseAPIView
from apps.subject.serializers.cohort_serializers import ErrorDetailStringSerializer


def error_response(*, message: str, http_status: int) -> Response:
    return Response({"error_detail": message}, status=http_status)


class DeploymentListAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 목록 조회 API",
        parameters=[DeploymentListQuerySerializer],
        responses={
            200: OpenApiResponse(response=DeploymentListResponseSerializer, description="OK"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
            404: OpenApiResponse(response=ErrorDetailStringSerializer, description="Not Found"),
        },
    )
    def get(self, request: Request) -> Response:
        query_serializer = DeploymentListQuerySerializer(data=request.query_params)
        query_serializer.is_valid()

        validated_data = query_serializer.validated_data

        page = validated_data.get("page", 1)
        status_value = validated_data.get("status", "all")

        try:
            user_id = request.user.id
            if user_id is None:
                return error_response(
                    message="사용자 정보를 찾을 수 없습니다.",
                    http_status=status.HTTP_404_NOT_FOUND,
                )

            result = ExamDeploymentService.get_user_deployments(
                user_id=user_id,
                page=page,
                status=status_value,
            )
        except DeploymentForbiddenError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_403_FORBIDDEN,
            )
        except UserNotFoundError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)


class DeploymentDetailAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 응시 문제풀이 API",
        responses={
            200: OpenApiResponse(response=DeploymentDetailResponseSerializer, description="OK"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
            404: OpenApiResponse(response=ErrorDetailStringSerializer, description="Not Found"),
            410: OpenApiResponse(response=ErrorDetailStringSerializer, description="Gone"),
        },
    )
    def get(self, request: Request, deployment_id: int) -> Response:
        user_id = request.user.id
        if user_id is None:
            return error_response(
                message="사용자 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = ExamDeploymentService.get_deployment_detail(
                user_id=user_id,
                deployment_id=deployment_id,
                verified=ExamDeploymentAccessService.is_verified(
                    deployment_id=deployment_id,
                    user_id=user_id,
                ),
            )
        except DeploymentForbiddenError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_403_FORBIDDEN,
            )
        except DeploymentNotFoundError:
            return error_response(
                message="해당 시험 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )
        except DeploymentGoneError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_410_GONE,
            )
        except UserNotFoundError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)


class DeploymentStatusAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 상태 확인 API",
        responses={
            200: OpenApiResponse(response=DeploymentStatusResponseSerializer, description="OK"),
            400: OpenApiResponse(response=ErrorDetailStringSerializer, description="Bad Request"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
            404: OpenApiResponse(response=ErrorDetailStringSerializer, description="Not Found"),
            410: OpenApiResponse(response=ErrorDetailStringSerializer, description="Gone"),
        },
    )
    def get(self, request: Request, deployment_id: int) -> Response:
        user_id = request.user.id
        if user_id is None:
            return error_response(
                message="사용자 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = ExamDeploymentService.get_deployment_status(
                user_id=user_id,
                deployment_id=deployment_id,
                verified=ExamDeploymentAccessService.is_verified(
                    deployment_id=deployment_id,
                    user_id=user_id,
                ),
            )
        except DeploymentInvalidSessionError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        except DeploymentForbiddenError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_403_FORBIDDEN,
            )
        except DeploymentNotFoundError:
            return error_response(
                message="해당 시험 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )
        except DeploymentGoneError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_410_GONE,
            )
        except UserNotFoundError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)
