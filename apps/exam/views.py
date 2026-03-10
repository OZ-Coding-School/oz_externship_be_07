import secrets
import string

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Avg, Count
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Exam, ExamDeployment, ExamQuestion, ExamSubmission
from .serializers import (
    ErrorDetailSerializer,
    ExamCreateSerializer,
    ExamDeleteRequestSerializer,
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
    ExamDetailSerializer,
    ExamListSerializer,
    ExamUpdateSerializer,
)


class ExamListCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="쪽지시험 목록 조회",
        description="관리자용 쪽지시험 목록을 조회합니다. 과목 필터 및 키워드 검색이 가능합니다.",
        responses={200: ExamListSerializer(many=True)},
        tags=["쪽지시험 관리"],
    )
    def get(self, request):
        # 검색/필터링 로직 (정의서 요구사항 반영)
        subject_id = request.query_params.get("subject_id")
        search_keyword = request.query_params.get("search_keyword")

        exams = Exam.objects.all().order_by("-created_at")

        if subject_id:
            exams = exams.filter(subject_id=subject_id)
        if search_keyword:
            exams = exams.filter(title__icontains=search_keyword)

        serializer = ExamListSerializer(exams, many=True)
        # 요구사항 정의서 Success Response Example 구조 반영
        return Response(
            {"page": 1, "size": 10, "total_count": exams.count(), "exams": serializer.data}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="쪽지시험 생성",
        description="새로운 쪽지시험을 생성합니다. 썸네일 이미지는 binary 파일로 전송해야 합니다.",
        request=ExamCreateSerializer,
        responses={201: ExamCreateSerializer},
        tags=["쪽지시험 관리"],
    )
    def post(self, request):
        serializer = ExamCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamDetailAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ExamDetailSerializer

    def get_object(self, exam_id):
        return Exam.objects.get(id=exam_id)

    @extend_schema(
        summary="쪽지시험 상세 조회",
        description="특정 ID의 쪽지시험 상세 정보와 질문 목록을 조회합니다.",
        responses={200: ExamDetailSerializer},
        tags=["쪽지시험 관리"],
    )
    def get(self, request, exam_id):
        exam = self.get_object(exam_id)
        serializer = ExamDetailSerializer(exam)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="쪽지시험 수정",
        description="기존 쪽지시험의 정보를 수정합니다. 이미지 변경이 없을 경우 필드를 비워둘 수 있습니다.",
        request=ExamUpdateSerializer,
        responses={200: ExamUpdateSerializer},
        tags=["쪽지시험 관리"],
    )
    def put(self, request, exam_id):
        exam = self.get_object(exam_id)
        serializer = ExamUpdateSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="쪽지시험 삭제",
        description="특정 쪽지시험을 삭제합니다. 성공 시 삭제된 시험의 ID를 반환합니다.",
        responses={201: ExamDeleteRequestSerializer},
        tags=["쪽지시험 관리"],
    )
    def delete(self, request, exam_id):
        exam = self.get_object(exam_id)
        exam.delete()
        return Response({"id": exam_id}, status=status.HTTP_200_OK)


class ExamDeploymentBaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExamDeployment.objects.select_related(
            "exam",
            "exam__subject",
            "cohort",
            "cohort__course",
        ).all()

    def get_object(self, pk):
        return self.get_queryset().get(pk=pk)

    @staticmethod
    def _generate_access_code(length=8):
        chars = string.digits + string.ascii_letters
        while True:
            code = "".join(secrets.choice(chars) for _ in range(length))
            if not ExamDeployment.objects.filter(access_code=code).exists():
                return code

    @staticmethod
    def _build_questions_snapshot(exam):
        questions = ExamQuestion.objects.filter(exam=exam).order_by("id")

        snapshot = []
        for q in questions:
            snapshot.append(
                {
                    "id": q.id,
                    "question": q.question,
                    "prompt": q.prompt,
                    "blank_count": q.blank_count,
                    "options_json": q.options_json,
                    "type": q.type,
                    "answer": q.answer,
                    "point": q.point,
                    "explanation": q.explanation,
                }
            )
        return snapshot

    @staticmethod
    def _get_total_student_count(cohort):
        candidate_names = [
            "cohort_students",
            "cohortstudent_set",
            "students",
        ]

        for name in candidate_names:
            relation = getattr(cohort, name, None)
            if relation is not None and hasattr(relation, "count"):
                return relation.count()

        return 0

    @staticmethod
    def _build_list_item(deployment):
        submit_count = getattr(deployment, "submit_count", None)
        if submit_count is None:
            submit_count = ExamSubmission.objects.filter(deployment=deployment).count()

        avg_score = getattr(deployment, "avg_score", None)
        if avg_score is None:
            avg_score = ExamSubmission.objects.filter(deployment=deployment).aggregate(avg=Avg("score"))["avg"] or 0

        subject = deployment.exam.subject
        cohort = deployment.cohort
        course = cohort.course

        return {
            "id": deployment.id,
            "submit_count": submit_count,
            "avg_score": round(float(avg_score), 1) if avg_score else 0.0,
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
    # =========================================================
    # 쪽지시험 배포 생성 API
    # POST /api/v1/admin/exams/deployments
    # =========================================================
    @extend_schema(
        tags=["Admin Exams Deployment"],
        summary="쪽지시험 배포 생성 API",
        request=ExamDeploymentCreateSerializer,
        responses={
            201: ExamDeploymentCreateResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
            409: ErrorDetailSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ExamDeploymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exam = serializer.validated_data["exam"]
        snapshot = self._build_questions_snapshot(exam)
        access_code = self._generate_access_code()

        deployment = serializer.save(
            access_code=access_code,
            questions_snapshot_json=snapshot,
        )

        response_serializer = ExamDeploymentCreateResponseSerializer({"pk": deployment.id})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # =========================================================
    # 쪽지시험 배포 목록 조회 API
    # GET /api/v1/admin/exams/deployments
    # =========================================================
    @extend_schema(
        tags=["Admin Exams Deployment"],
        summary="쪽지시험 배포 목록 조회 API",
        responses={
            200: ExamDeploymentListResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        query_serializer = ExamDeploymentListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        queryset = self.get_queryset().annotate(
            submit_count=Count("examsubmission", distinct=True),
            avg_score=Avg("examsubmission__score"),
        )

        search_keyword = params.get("search_keyword")
        subject_id = params.get("subject_id")
        cohort_id = params.get("cohort_id")
        sort = params.get("sort")
        order = params.get("order", "desc")
        page = params.get("page", 1)
        size = params.get("size", 10)

        if search_keyword:
            queryset = queryset.filter(exam__title__icontains=search_keyword)

        if subject_id:
            queryset = queryset.filter(exam__subject_id=subject_id)

        if cohort_id:
            queryset = queryset.filter(cohort_id=cohort_id)

        sort_map = {
            "created_at": "created_at",
            "submit_count": "submit_count",
            "avg_score": "avg_score",
        }
        sort_field = sort_map.get(sort, "created_at")

        if order == "asc":
            queryset = queryset.order_by(sort_field, "id")
        else:
            queryset = queryset.order_by(f"-{sort_field}", "-id")

        paginator = Paginator(queryset, size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        results = [self._build_list_item(obj) for obj in page_obj.object_list]

        base_path = request.path
        previous_url = None
        next_url = None

        if page_obj.has_previous():
            previous_url = f"{base_path}?page={page_obj.previous_page_number()}&size={size}"

        if page_obj.has_next():
            next_url = f"{base_path}?page={page_obj.next_page_number()}&size={size}"

        response_data = {
            "count": paginator.count,
            "previous": previous_url,
            "next": next_url,
            "results": results,
        }

        response_serializer = ExamDeploymentListResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ExamDeploymentDetailAPIView(ExamDeploymentBaseAPIView):
    # =========================================================
    # 쪽지시험 배포 상세 조회 API
    # GET /api/v1/admin/exams/deployments/{deployment_id}
    # =========================================================
    @extend_schema(
        tags=["Admin Exams Deployment"],
        summary="쪽지시험 배포 상세 조회 API",
        responses={
            200: ExamDeploymentDetailSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        deployment = self.get_object(pk)

        submit_count = ExamSubmission.objects.filter(deployment=deployment).count()
        total_student_count = self._get_total_student_count(deployment.cohort)
        not_submitted_count = max(total_student_count - submit_count, 0)

        cohort = deployment.cohort
        course = cohort.course
        subject = deployment.exam.subject

        response_data = {
            "id": deployment.id,
            "exam_access_url": f"/api/v1/exams/deployments/{deployment.id}",
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
            "open_at": deployment.open_at.strftime("%Y-%m-%d %H:%M:%S"),
            "close_at": deployment.close_at.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": deployment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
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

        response_serializer = ExamDeploymentDetailSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # =========================================================
    # 쪽지시험 배포 정보 수정 API
    # PATCH /api/v1/admin/exams/deployments/{deployment_id}
    # =========================================================
    @extend_schema(
        tags=["Admin Exams Deployment"],
        summary="쪽지시험 배포 정보 수정 API",
        request=ExamDeploymentUpdateSerializer,
        responses={
            200: ExamDeploymentUpdateResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
        },
    )
    def patch(self, request, pk=None, *args, **kwargs):
        instance = self.get_object(pk)
        serializer = ExamDeploymentUpdateSerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = ExamDeploymentUpdateResponseSerializer(
            {
                "deployment_id": instance.id,
                "duration_time": instance.duration_time,
                "open_at": instance.open_at.strftime("%Y-%m-%d %H:%M:%S"),
                "close_at": instance.close_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": instance.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # =========================================================
    # 쪽지시험 배포 삭제 API
    # DELETE /api/v1/admin/exams/deployments/{deployment_id}
    # =========================================================
    @extend_schema(
        tags=["Admin Exams Deployment"],
        summary="쪽지시험 배포 삭제 API",
        responses={
            200: ExamDeploymentDeleteResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
            409: ErrorDetailSerializer,
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        deployment = self.get_object(pk)
        deployment.delete()

        response_serializer = ExamDeploymentDeleteResponseSerializer({"detail": "쪽지시험 배포가 삭제되었습니다."})
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ExamDeploymentStatusUpdateAPIView(ExamDeploymentBaseAPIView):
    # =========================================================
    # 쪽지시험 배포 on/off API
    # PATCH /api/v1/admin/exams/deployments/{deployment_id}/status
    # =========================================================
    @extend_schema(
        tags=["Admin Exams Deployment"],
        summary="쪽지시험 배포 on/off API",
        request=ExamDeploymentStatusUpdateSerializer,
        responses={
            200: ExamDeploymentStatusUpdateResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
            409: ErrorDetailSerializer,
        },
    )
    def patch(self, request, pk=None, *args, **kwargs):
        deployment = self.get_object(pk)
        serializer = ExamDeploymentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deployment.status = serializer.validated_data["status"]
        deployment.save(update_fields=["status", "updated_at"])

        response_serializer = ExamDeploymentStatusUpdateResponseSerializer(
            {
                "deployment_id": deployment.id,
                "status": deployment.status,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)