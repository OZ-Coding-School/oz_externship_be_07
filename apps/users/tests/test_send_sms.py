import random

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SendSmsTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("users:sms-send")
        middle = random.randint(1000, 9999)
        last = random.randint(1000, 9999)
        self.valid_phone = f"010-{middle}-{last}"
        cache.clear()

    def test_send_sms_success(self) -> None:
        response = self.client.post(self.url, {"phone_number": self.valid_phone}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "인증 코드가 전송 되었습니다.")

        clean_number = "".join(filter(str.isdigit, self.valid_phone))
        self.assertTrue(cache.get(f"limit_sms:{clean_number}"))

    def test_send_sms_fail_field(self) -> None:
        response = self.client.post(self.url, {"phone_number": "안녕-하세요-ㅋㅋ"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_sms_throttled(self) -> None:
        clean_number = "".join(filter(str.isdigit, self.valid_phone))
        cache.set(f"limit_sms:{clean_number}", True, timeout=60)

        response = self.client.post(self.url, {"phone_number": self.valid_phone}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
