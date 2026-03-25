import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ProfileAPITest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="king2jun@jjang.com",
            nickname="킹왕이준",
            phone_number=f"010{uuid.uuid4().hex[:8]}",
            password="password123",
            birthday="1998-08-12",
            gender="M",
        )
        self.other_user = User.objects.create_user(
            email="iamzizon@somin.com",
            nickname="지존소민",
            phone_number=f"010{uuid.uuid4().hex[:8]}",
            password="password123",
            birthday="1999-02-04",
            gender="F",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("users:profile")

    def test_get_profile(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "킹왕이준")

    def test_patch_profile_success(self) -> None:
        data = {"nickname": "화난이준"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "화난이준")

    def test_patch_profile_image_success(self) -> None:
        url = reverse("users:profile-image")
        image_url = "https://oz-externship.s3.ap-northeast-2.amazonaws.com/uploads/images/profiles/photo.png"
        data = {"profile_img_url": image_url}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile_img_url"], image_url)

    def test_patch_profile_conflict(self) -> None:
        data = {"nickname": "지존소민"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_nickname_check_available(self) -> None:
        url = reverse("users:check-nickname")
        data = {"nickname": "침울현오"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "사용가능한 닉네임 입니다.")

    def test_nickname_check_conflict(self) -> None:
        url = reverse("users:check-nickname")
        data = {"nickname": "지존소민"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
