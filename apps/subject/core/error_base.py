from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class SubjectBaseAPIView(APIView):
    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if isinstance(exc, exceptions.PermissionDenied):
            return Response(
                {"error_detail": str(exc.detail)},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().handle_exception(exc)
