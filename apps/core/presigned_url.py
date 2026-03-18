import uuid
from typing import Any

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


class BasePresignedUrlView(APIView):
    permission_classes = [IsAuthenticated]
    folder: str = ""

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        file_name = request.data.get("file_name")
        extension = str(file_name).split(".")[-1].lower() if file_name else ""

        if not file_name or extension not in ALLOWED_EXTENSIONS:
            return Response(
                {"error_detail": "지원하지 않는 파일 형식입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        key = f"uploads/images/{self.folder}/{uuid.uuid4()}.{extension}"

        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        )

        try:
            presigned_url = s3_client.generate_presigned_url(
                "put_object",
                Params={"Bucket": settings.AWS_S3_BUCKET_NAME, "Key": key},
                ExpiresIn=300,
            )
        except ClientError:
            return Response(
                {"error_detail": "Presigned URL 생성에 실패했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        img_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{key}"

        return Response(
            {
                "presigned_url": presigned_url,
                "img_url": img_url,
                "key": key,
            },
            status=status.HTTP_200_OK,
        )
