from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.enroll_student import EnrollStudentSerializer


class EnrollStudentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        return super().handle_exception(exc)

    @extend_schema(
        summary="수강생 등록 신청 API",
        tags=["Accounts"],
        request=EnrollStudentSerializer,
        responses={
            201: OpenApiResponse(description="수강생 등록 신청완료."),
            400: OpenApiResponse(description="이 필드는 필수 항목입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = EnrollStudentSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # save() 시 user를 넘겨주는 로직은 유지합니다.
        serializer.save(user=request.user)

        return Response({"detail": "수강생 등록 신청완료."}, status=status.HTTP_201_CREATED)
