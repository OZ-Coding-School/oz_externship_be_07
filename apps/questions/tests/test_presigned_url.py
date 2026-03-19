from datetime import date
from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.models import User


def make_mock_s3() -> MagicMock:
    mock_instance = MagicMock()
    mock_instance.generate_presigned_url.return_value = "https://mock-bucket.s3.amazonaws.com/mock-key"
    return mock_instance


class AnswerPresignedUrlTest(TestCase):
    user: User
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="presigned@example.com",
            nickname="프리사인드",
            name="테스트유저",
            phone_number="010-0002-0001",
            gender="MALE",
            birthday=date(2000, 1, 1),
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # 미인증 → 401
    def test_presigned_url_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response = self.client.put(
            "/api/v1/qna/answers/presigned-url",
            {"file_name": "test.png"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 지원하지 않는 확장자 → 400
    def test_presigned_url_invalid_extension(self) -> None:
        response = self.client.put(
            "/api/v1/qna/answers/presigned-url",
            {"file_name": "test.gif"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "지원하지 않는 파일 형식입니다.")

    # 파일명 없음 → 400
    def test_presigned_url_no_file_name(self) -> None:
        response = self.client.put(
            "/api/v1/qna/answers/presigned-url",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "지원하지 않는 파일 형식입니다.")

    # S3 실패 → 400
    def test_presigned_url_s3_error(self) -> None:
        from botocore.exceptions import ClientError

        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket", "Message": "bucket not found"}},
            "generate_presigned_url",
        )
        with patch("apps.core.utils.s3_handler.boto3.client", return_value=mock_s3):
            response = self.client.put(
                "/api/v1/qna/answers/presigned-url",
                {"file_name": "test.png"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
