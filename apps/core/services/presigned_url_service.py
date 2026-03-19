import uuid
from typing import TypedDict

from botocore.exceptions import ClientError
from rest_framework.exceptions import ValidationError

from apps.core.utils.s3_handler import S3Handler

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


class PresignedUrlResult(TypedDict):
    presigned_url: str
    img_url: str
    key: str


class PresignedUrlService:

    # presigned URL 생성
    @staticmethod
    def create(folder: str, file_name: str) -> PresignedUrlResult:
        extension = file_name.split(".")[-1].lower()

        if not extension or extension not in ALLOWED_EXTENSIONS:
            raise ValidationError("지원하지 않는 파일 형식입니다.")

        key = f"uploads/images/{folder}/{uuid.uuid4()}.{extension}"
        content_type = f"image/{extension}"

        handler = S3Handler()
        try:
            presigned_url = handler.generate_presigned_url(key=key, content_type=content_type)
        except ClientError:
            raise ValidationError("Presigned URL 생성에 실패했습니다.")

        img_url = handler.get_img_url(key=key)

        return PresignedUrlResult(
            presigned_url=presigned_url,
            img_url=img_url,
            key=key,
        )
