from django.core.paginator import EmptyPage, Paginator
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.exam.models.exam_submission_models import ExamSubmission

from apps.exam.serializers.exam_deployment_serializers import (
    ErrorDetailSerializer,
    ExamDeploymentCreateResponseSerializer,
    ExamDeploymentCreateSerializer,
    ExamDeploymentDeleteResponseSerializer,
    ExamDeploymentDetailSerializer,
    ExamDeploymentListQuerySerializer,
    ExamDeploymentListResponseSerializer,
    ExamDeploymentStatusUpdateResponseSerializer,
    ExamDeploymentStatusUpdateSerializer,
    ExamDeploymentUpdateResponseSerializer,
    ExamDeploymentUpdateSerializer,
)

from apps.exam.servieces.exam_deployment_services import ExamDeploymentService


class ExamDeploymentBaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _build_list_item(self, deployment):
        """목록 조회를 위한 데이터 포맷팅 (View 전용 가공)"""
        subject = deployment.exam.subject
        cohort = deployment.cohort
        course = cohort.course

        return {
            "id": deployment.id,
            "submit_count": getattr(deployment, "submit_count", 0),
            "avg_score": round(float(getattr(deployment, "avg_score", 0.0)), 1),
            "status": deployment.status,
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
            "created_at": deployment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class ExamDeploymentListCreateAPIView(ExamDeploymentBaseAPIView):
    @extend_schema(
        tags=["쪽지시험 배포 관리"],
        summary="쪽지시험 배포 생성 API",
        request=ExamDeploymentCreateSerializer,
        responses={201: ExamDeploymentCreateResponseSerializer, 400: ErrorDetailSerializer},
    )
    def post(self, request, *args, **kwargs):
        """배포 생성 로직을 Service로 위임합니다."""
        serializer = ExamDeploymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Service를 통해 스냅샷 생성 및 액세스 코드 생성을 처리합니다.
        deployment = ExamDeploymentService.create_deployment(serializer.validated_data)

        response_serializer = ExamDeploymentCreateResponseSerializer({"pk": deployment.id})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["쪽지시험 배포 관리"],
        summary="쪽지시험 배포 목록 조회 API",
        responses={200: ExamDeploymentListResponseSerializer},
    )
    def get(self, request, *args, **kwargs):
        """통계 정보가 포함된 Queryset을 Service로부터 받아와 필터링 및 페이징을 수행합니다."""
        query_serializer = ExamDeploymentListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        # Service에서 annotate(submit_count, avg_score)가 적용된 쿼리셋을 가져옵니다.
        queryset = ExamDeploymentService.get_deployment_list_queryset()

        # 필터링 로직
        if params.get("search_keyword"):
            queryset = queryset.filter(exam__title__icontains=params["search_keyword"])
        if params.get("subject_id"):
            queryset = queryset.filter(exam__subject_id=params["subject_id"])
        if params.get("cohort_id"):
            queryset = queryset.filter(cohort_id=params["cohort_id"])

        # 정렬 로직
        sort_field = params.get("sort", "created_at")
        order = params.get("order", "desc")
        prefix = "-" if order == "desc" else ""
        queryset = queryset.order_by(f"{prefix}{sort_field}", f"{prefix}id")

        # 페이징 처리
        paginator = Paginator(queryset, params.get("size", 10))
        page_obj = paginator.get_page(params.get("page", 1))

        results = [self._build_list_item(obj) for obj in page_obj.object_list]

        response_data = {
            "count": paginator.count,
            "previous": (
                request.build_absolute_uri(page_obj.previous_page_number()) if page_obj.has_previous() else None
            ),
            "next": request.build_absolute_uri(page_obj.next_page_number()) if page_obj.has_next() else None,
            "results": results,
        }

        return Response(ExamDeploymentListResponseSerializer(response_data).data, status=status.HTTP_200_OK)


class ExamDeploymentDetailAPIView(ExamDeploymentBaseAPIView):
    @extend_schema(
        tags=["쪽지시험 배포 관리"],
        summary="쪽지시험 배포 상세 조회 API",
        responses={200: ExamDeploymentDetailSerializer},
    )
    def get(self, request, pk=None, *args, **kwargs):
        """상세 정보 조회를 위해 최적화된 Service 쿼리셋을 사용합니다."""
        deployment = ExamDeploymentService.get_deployment_list_queryset().get(pk=pk)

        # 응시 현황 계산
        submit_count = ExamSubmission.objects.filter(deployment=deployment).count()
        total_student_count = ExamDeploymentService.get_total_student_count(deployment.cohort)
        not_submitted_count = max(total_student_count - submit_count, 0)

        response_data = {
            "id": deployment.id,
            "exam_access_url": f"/api/v1/exams/deployments/{deployment.id}",
            "access_code": deployment.access_code,
            "cohort": {
                "id": deployment.cohort.id,
                "number": deployment.cohort.number,
                "display": f"{deployment.cohort.course.name} {deployment.cohort.number}기",
                "course": {
                    "id": deployment.cohort.course.id,
                    "name": deployment.cohort.course.name,
                    "tag": deployment.cohort.course.tag,
                },
            },
            "submit_count": submit_count,
            "not_submitted_count": not_submitted_count,
            "duration_time": deployment.duration_time,
            "open_at": deployment.open_at.strftime("%Y-%m-%d %H:%M:%S"),
            "close_at": deployment.close_at.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": deployment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "exam": {
                "id": deployment.exam.id,
                "title": deployment.exam.title,
                "thumbnail_img_url": deployment.exam.thumbnail_img_url,
            },
            "subject": {
                "id": deployment.exam.subject.id,
                "name": deployment.exam.subject.title,
            },
        }

        return Response(ExamDeploymentDetailSerializer(response_data).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["쪽지시험 배포 관리"],
        summary="쪽지시험 배포 정보 수정 API",
        request=ExamDeploymentUpdateSerializer,
        responses={200: ExamDeploymentUpdateResponseSerializer},
    )
    def patch(self, request, pk=None, *args, **kwargs):
        """부분 수정을 수행합니다."""
        instance = ExamDeploymentService.get_deployment_list_queryset().get(pk=pk)
        serializer = ExamDeploymentUpdateSerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            ExamDeploymentUpdateResponseSerializer(
                {
                    "deployment_id": instance.id,
                    "duration_time": instance.duration_time,
                    "open_at": instance.open_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "close_at": instance.close_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": instance.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            ).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["쪽지시험 배포 관리"],
        summary="쪽지시험 배포 삭제 API",
        responses={200: ExamDeploymentDeleteResponseSerializer},
    )
    def delete(self, request, pk=None, *args, **kwargs):
        """배포 삭제를 처리합니다."""
        deployment = ExamDeploymentService.get_deployment_list_queryset().get(pk=pk)
        deployment.delete()

        return Response({"detail": "쪽지시험 배포가 삭제되었습니다."}, status=status.HTTP_200_OK)


class ExamDeploymentStatusUpdateAPIView(ExamDeploymentBaseAPIView):
    @extend_schema(
        tags=["쪽지시험 배포 관리"],
        summary="쪽지시험 배포 on/off API",
        request=ExamDeploymentStatusUpdateSerializer,
        responses={200: ExamDeploymentStatusUpdateResponseSerializer},
    )
    def patch(self, request, pk=None, *args, **kwargs):
        """상태(Activated/Deactivated) 업데이트를 수행합니다."""
        deployment = ExamDeploymentService.get_deployment_list_queryset().get(pk=pk)
        serializer = ExamDeploymentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deployment.status = serializer.validated_data["status"]
        deployment.save(update_fields=["status", "updated_at"])

        return Response(
            ExamDeploymentStatusUpdateResponseSerializer(
                {
                    "deployment_id": deployment.id,
                    "status": deployment.status,
                }
            ).data,
            status=status.HTTP_200_OK,
        )
