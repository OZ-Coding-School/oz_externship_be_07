from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PhoneChangeAPITest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="giveup@gg.com",
            nickname="무너진현오",
            phone_number="01011112222",
            password="password123",
            birthday="2000-09-25",
            gender="M",
        )
        self.other_user = User.objects.create_user(
            email="tekai@wall.com",
            nickname="버티는고건님",
            phone_number="01099998888",
            password="password123",
            birthday="2000-09-25",
            gender="M",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("users:change-phone")

    def test_phone_change_success(self) -> None:
        new_number = "01055556666"
        data = {"phone_verify_token": "valid_token_123", "phone_number": new_number}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "휴대폰 번호 변경에 성공하였습니다.")
        self.assertEqual(response.data["phone_number"], new_number)

        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, new_number)

    def test_phone_change_conflict(self) -> None:
        data = {"phone_verify_token": "valid_token_123", "phone_number": "01099998888"}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error_detail"], "이미 등록된 휴대폰 번호입니다.")

    def test_phone_change_invalid_token(self) -> None:
        data = {"phone_verify_token": "invalid_token", "phone_number": "01055556666"}
        response = self.client.patch(self.url, data)

        self.assertTrue(status.is_client_error(response.status_code))

    def test_phone_change_unauthorized(self) -> None:
        self.client.force_authenticate(user=None)
        data = {"phone_verify_token": "token", "phone_number": "01055556666"}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
