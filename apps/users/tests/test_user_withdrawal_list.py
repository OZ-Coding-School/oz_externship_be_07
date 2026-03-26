from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.choices import UserRole, UserStatus, WithdrawalReason
from apps.users.models.models import User, Withdrawal


class AdminUserWithdrawalGetTest(TestCase):
    admin_user: User
    normal_user: User
    withdrawal: Withdrawal
    client: APIClient

    LIST_URL_NAME: str = "admin-withdrawal-list"
    DETAIL_URL_NAME: str = "admin-withdrawal-detail"

    @classmethod
    def setUpTestData(cls) -> None:
        # 관리자 생성
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            name="Nice",
            nickname="Yeah",
            phone_number="01011112222",
            birthday="19900101",
            role=UserRole.ADMIN,
            is_staff=True,
        )

        # 유저 생성
        cls.normal_user = User.objects.create_user(
            email="user@example.com",
            name="우와아",
            nickname="머리아파아",
            phone_number="01033334444",
            birthday="19950505",
            status=UserStatus.WITHDREW,
            is_active=False,
        )

        # 탈퇴 정보 생성
        cls.withdrawal = Withdrawal.objects.create(
            user=cls.normal_user,
            reason=WithdrawalReason.NO_LONGER_NEEDED,
            reason_detail="개인 사정",
            due_date="2026-04-24",
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_withdrawal_list_success_200(self) -> None:
        """목록 조회 성공 테스트"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(self.LIST_URL_NAME)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["user"]["name"], "우와아")

    def test_get_withdrawal_list_filter_search(self) -> None:
        """이름 검색 필터링 테스트"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(self.LIST_URL_NAME)

        response = self.client.get(url, {"search": "우와아"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["user"]["name"], "우와아")

    def test_get_withdrawal_detail_success_200(self) -> None:
        """상세 조회 성공 테스트"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(self.DETAIL_URL_NAME, kwargs={"withdrawal_id": self.withdrawal.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.withdrawal.id)
        self.assertEqual(response.data["user"]["name"], "우와아")
        self.assertIn("assigned_courses", response.data)

    def test_get_withdrawal_detail_fail_404(self) -> None:
        """존재하지 않는 ID로 상세 조회 시 404 확인"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(self.DETAIL_URL_NAME, kwargs={"withdrawal_id": 99999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", response.data)

    def test_get_withdrawal_fail_403_forbidden(self) -> None:
        """비권한 유저 접근 차단 테스트"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse(self.LIST_URL_NAME)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")
