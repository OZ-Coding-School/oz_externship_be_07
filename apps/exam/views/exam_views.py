from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from apps.exam.serializers.exam_serializers import (
    ExamCreateSerializer,
    ExamDeleteRequestSerializer,
    ExamDetailSerializer,
    ExamListSerializer,
    ExamUpdateSerializer,
    ExamDeleteRequestSerializer,
)
from apps.exam.servieces.exam_services import ExamService


class ExamListCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="쪽지시험 목록 조회",
        description="관리자용 쪽지시험 목록을 조회합니다. 과목 필터 및 키워드 검색이 가능합니다.",
        responses={200: ExamListSerializer(many=True)},
        tags=["쪽지시험 관리"],
    )
    def get(self, request):
        exams = ExamService.get_exam_list(
            subject_id=request.query_params.get("subject_id"), search_keyword=request.query_params.get("search_keyword")
        )
        serializer = ExamListSerializer(exams, many=True)

        # 정의서 요구사항에 따른 공통 응답 구조 유지
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
        serializer.is_valid(raise_exception=True)

        # Service를 통해 S3 경로 생성 및 DB 저장
        exam = ExamService.create_exam(serializer.validated_data)
        return Response(ExamCreateSerializer(exam).data, status=status.HTTP_201_CREATED)


class ExamDetailAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="쪽지시험 상세 조회",
        description="특정 ID의 쪽지시험 상세 정보와 질문 목록을 조회합니다.",
        responses={200: ExamDetailSerializer},
        tags=["쪽지시험 관리"],
    )
    def get(self, request, exam_id):
        # Service를 통해 객체 조회
        exam = ExamService.get_exam_list().get(id=exam_id)
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
        serializer = ExamUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Service를 통해 이미지 및 필드 수정
        exam = ExamService.update_exam(exam_id, serializer.validated_data)
        return Response(ExamUpdateSerializer(exam).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="쪽지시험 삭제",
        description="특정 쪽지시험을 삭제합니다. 성공 시 삭제된 시험의 ID를 반환합니다.",
        responses={200: ExamDeleteRequestSerializer},
        tags=["쪽지시험 관리"],
    )
    def delete(self, request, exam_id):
        deleted_id = ExamService.delete_exam(exam_id)
        return Response({"id": deleted_id}, status=status.HTTP_200_OK)
