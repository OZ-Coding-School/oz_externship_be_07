from typing import Any

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.exam.core.common import error_response
from apps.exam.core.exceptions import (
    CodeMismatchError,
    DeploymentForbiddenError,
    DeploymentLockedError,
    DeploymentNotFoundError,
    UserNotFoundError,
)
from apps.exam.serializers.deployment_serializers import (
    DeploymentCheckCodeRequestSerializer,
)
from apps.exam.services.exam_deployment_access_services import (
    ExamDeploymentAccessService,
)
from apps.subject.core.error_base import SubjectBaseAPIView
from apps.subject.serializers.cohort_serializers import (
    ErrorDetailFieldSerializer,
    ErrorDetailStringSerializer,
)


def field_error_response(*, errors: dict[str, Any], http_status: int = status.HTTP_400_BAD_REQUEST) -> Response:
    normalized_errors: dict[str, Any] = {}

    for field, value in errors.items():
        if isinstance(value, list) and value:
            normalized_errors[field] = value[0]
        else:
            normalized_errors[field] = value

    return Response({"error_detail": normalized_errors}, status=http_status)


class DeploymentCheckCodeAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Exams"],
        summary="쪽지시험 참가 코드 검증 API",
        request=DeploymentCheckCodeRequestSerializer,
        responses={
            204: OpenApiResponse(description="No Content"),
            400: OpenApiResponse(response=ErrorDetailFieldSerializer, description="Bad Request"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
            404: OpenApiResponse(response=ErrorDetailStringSerializer, description="Not Found"),
            423: OpenApiResponse(response=ErrorDetailStringSerializer, description="Locked"),
        },
        examples=[
            OpenApiExample(
                "request example",
                value={"code": "124312"},
                request_only=True,
            ),
            OpenApiExample(
                "code mismatch example",
                value={"error_detail": "응시 코드가 일치하지 않습니다."},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "field error example",
                value={"error_detail": {"code": "이 필드는 필수 항목입니다."}},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request: Request, deployment_id: int) -> Response:
        serializer = DeploymentCheckCodeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return field_error_response(errors=dict(serializer.errors))

        user_id = request.user.id
        if user_id is None:
            return error_response(
                message="사용자 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        try:
            ExamDeploymentAccessService.check_deployment_code(
                user_id=user_id,
                deployment_id=deployment_id,
                code=serializer.validated_data["code"],
            )
        except CodeMismatchError as exc:
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
                message="배포 정보를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )
        except DeploymentLockedError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_423_LOCKED,
            )
        except UserNotFoundError as exc:
            return error_response(
                message=str(exc),
                http_status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
