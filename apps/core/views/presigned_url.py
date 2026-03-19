from typing import Any

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers.presigned_url_serializer import PresignedUrlRequestSerializer
from apps.core.services.presigned_url_service import PresignedUrlService


class BasePresignedUrlView(APIView):
    permission_classes = [IsAuthenticated]
    folder: str = ""

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = PresignedUrlRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": "지원하지 않는 파일 형식입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = PresignedUrlService.create(
                folder=self.folder,
                file_name=serializer.validated_data["file_name"],
            )
        except ValidationError as e:
            error_msg = str(list(e.detail.values())[0]) if isinstance(e.detail, dict) else str(e.detail[0])
            return Response(
                {"error_detail": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"error_detail": "Presigned URL 생성에 실패했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_200_OK)
