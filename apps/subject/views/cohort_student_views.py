from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subject.core.permissions import IsStaffUser
from apps.subject.serializers.cohort_student_serializers import (
    StudentSubjectScoreItemSerializer,
)
from apps.subject.services.cohort_student_services import CohortStudentService


# 2. 학생별 점수 조회
class StudentScoreAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        tags=["admin_students"],
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
