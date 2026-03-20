from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from .error_custom_base import ConflictException

class ExamBaseAPIView(APIView):
    validation_error_msgs = {
        "GET": "유효하지 않은 조회 요청입니다.",
        "POST": "유효하지 않은 생성 요청입니다.",
        "PUT": "유효하지 않은 수정 요청입니다.",
        "DELETE": "유효하지 않은 삭제 요청입니다.",
    }
    permission_error_msgs = {
        "GET": "유효하지 않은 조회 요청입니다.",
        "POST": "유효하지 않은 생성 요청입니다.",
        "PUT": "유효하지 않은 수정 요청입니다.",
        "DELETE": "유효하지 않은 삭제 요청입니다.",
    }
    def handle_exception(self, exc: Exception) -> Response:
        print(f"!!! 핸들러 작동 중: {type(exc)} !!!")
        if isinstance(exc, exceptions.ValidationError):
            method = self.request.method
            error_msg = self.validation_error_msgs.get(method, "유효하지 않은 요청입니다.")

            return Response(
                {"error_detail": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if isinstance(exc, exceptions.PermissionDenied):
            method = self.request.method
            error_msg = self.permission_error_msgs.get(method)

            if not error_msg:
                error_msg = "유효하지 않은 요청입니다."

            return Response(
                {"error_detail": error_msg},
                status=status.HTTP_403_FORBIDDEN,
            )

        if isinstance(exc, (exceptions.NotFound, Http404)):
            detail = str(exc.detail) if hasattr(exc, 'detail') else "해당 정보를 찾을 수 없습니다."
            return Response(
                {"error_detail": detail},
                status=status.HTTP_404_NOT_FOUND,
            )

        if isinstance(exc, ConflictException):
            return Response(
                {"error_detail": str(exc.detail)},
                status=status.HTTP_409_CONFLICT,
            )

        return super().handle_exception(exc)
