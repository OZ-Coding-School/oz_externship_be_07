import datetime
import random
from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class SendEmailTest(APITestCase):
    user: Any
    url: str
    valid_email: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("users:email-send")
        cls.valid_email = "user@example.com"
        cls.user = User.objects.create_user(
            email=cls.valid_email,
            password="oldPassword123!",
            name="테스터",
            nickname="tester",
            phone_number="010-1111-2223",
            gender="M",
            birthday=datetime.date(1995, 5, 5),
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def tearDown(self) -> None:
        cache.clear()

    @patch("apps.users.services.verification_services.send_mail")
    def test_send_email_success(self, mock_send_email: MagicMock) -> None:
        response = self.client.post(self.url, {"email": self.valid_email}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "이메일 인증 코드가 전송되었습니다.")
        self.assertTrue(mock_send_email.called)
        self.assertIsNotNone(cache.get(f"verify:{self.valid_email}"))

    def test_send_email_fail_field_missing(self) -> None:
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"]["email"][0], "이 필드는 필수 항목입니다.")

    def test_send_email_fail_invalid_format(self) -> None:
        response = self.client.post(self.url, {"email": "invalid-email-format"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("올바른 이메일 형식이 아닙니다.", str(response.data["error_detail"]["email"][0]))


class EmailVerifyTest(APITestCase):
    email: str
    code: str
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.email = "tester@example.com"
        cls.code = "Abc456"

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("users:email-verify")

        cache.clear()
        cache.set(f"verify:{self.email}", self.code, timeout=300)

    def test_verify_email_success(self) -> None:
        data: dict[str, Any] = {"email": self.email, "code": self.code}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "이메일 인증에 성공하였습니다.")
        self.assertIn("email_token", response.data)
        self.assertEqual(len(response.data["email_token"]), 32)

        self.assertIsNone(cache.get(f"verify:{self.email}"))

    def test_verify_email_wrong_code(self) -> None:
        data: dict[str, Any] = {"email": self.email, "code": "999999"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("인증번호가 일치하지 않습니다.", str(response.data["error_detail"]["code"]))

    def test_verify_email_expired_code(self) -> None:
        data: dict[str, Any] = {"email": "no-requested@example.com", "code": self.code}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("인증 시간이 만료되었거나 잘못된 요청입니다.", str(response.data["error_detail"]["code"]))

    def test_verify_email_invalid_format(self) -> None:
        data: dict[str, Any] = {"email": self.email, "code": "ab#123"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("인증번호는 영문과 숫자만 입력 가능합니다.", str(response.data["error_detail"]["code"]))

    def test_verify_email_brute_force_protection(self) -> None:
        data = {"email": self.email, "code": "999999"}

        for _ in range(4):
            self.client.post(self.url, data, format="json")

        response = self.client.post(self.url, data, format="json")

        self.assertTrue(
            "인증 번호 5회 실패" in str(response.data) or "인증 시간이 만료되었거나" in str(response.data),
            f"예상치 못한 에러 발생: {response.data}",
        )
        final_response = self.client.post(self.url, data, format="json")
        self.assertEqual(final_response.status_code, status.HTTP_400_BAD_REQUEST)


class SendSmsTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("users:sms-send")
        middle = random.randint(1000, 9999)
        last = random.randint(1000, 9999)
        self.valid_phone = f"010-{middle}-{last}"
        cache.clear()

    @patch("apps.users.services.verification_services.Client")
    def test_send_sms_success(self, mock_send_sms: MagicMock) -> None:
        response = self.client.post(self.url, {"phone_number": self.valid_phone}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "인증 코드가 전송 되었습니다.")
        self.assertTrue(mock_send_sms.called)

        phone_number = self.valid_phone.replace("-", "")
        self.assertIsNotNone(cache.get(f"limit_sms:{phone_number}"))

    def test_send_sms_fail_field(self) -> None:
        response = self.client.post(self.url, {"phone_number": "안녕-하세요-ㅋㅋ"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_sms_throttled(self) -> None:
        clean_number = "".join(filter(str.isdigit, self.valid_phone))
        cache.set(f"limit_sms:{clean_number}", True, timeout=60)

        response = self.client.post(self.url, {"phone_number": self.valid_phone}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class SmsVerifyTest(APITestCase):
    url: str
    valid_phone: str
    invalid_code: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("users:sms-verify")
        cls.valid_phone = "010-2234-5678"
        cls.invalid_code = "000000"

    def setUp(self) -> None:
        cache.clear()

    @patch("apps.users.services.verification_services.Client")
    def test_verify_sms_success(self, mock_twilio_client: MagicMock) -> None:
        mock_check = MagicMock()
        mock_check.status = "approved"

        mock_twilio_client.return_value.verify.v2.services.return_value.verification_checks.create.return_value = (
            mock_check
        )

        data = {"phone_number": "010-1234-5678", "code": "123456"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sms_token", response.data)

        sms_token = response.data["sms_token"]
        self.assertEqual(cache.get(f"sms_token:{sms_token}"), "01012345678")

    def test_verify_sms_fail_field(self) -> None:
        data = {"phone_number": "010-123", "code": "123456"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data["error_detail"])

    def test_verify_sms_no_code(self) -> None:
        data = {"phone_number": self.valid_phone}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
