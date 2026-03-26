from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.users.choices import UserRole, UserStatus
from apps.users.models.models import User, Withdrawal, WithdrawalReason


class WithdrawalAnalyticsAPITestCase(APITestCase):
    admin_user: User
    now: datetime
    one_month_ago: datetime

    @classmethod
    def setUpTestData(cls) -> None:
        user_manager = User.objects
        cls.admin_user = user_manager.create(
            email="admin@example.com",
            nickname="웅냥냥",
            name="우에엥",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVATED,
            birthday="1990-01-01",
            phone_number="01000000000",
        )

        cls.now = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        cls.one_month_ago = cls.now - timedelta(days=30)

        w1 = Withdrawal.objects.create(reason=WithdrawalReason.TECHNICAL_ISSUES, due_date=cls.one_month_ago.date())
        w2 = Withdrawal.objects.create(reason=WithdrawalReason.TECHNICAL_ISSUES, due_date=cls.one_month_ago.date())
        Withdrawal.objects.filter(id__in=[w1.id, w2.id]).update(created_at=cls.one_month_ago)
        w3 = Withdrawal.objects.create(reason=WithdrawalReason.OTHER, due_date=cls.now.date())
        Withdrawal.objects.filter(id=w3.id).update(created_at=cls.now)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_date_range_filtering_logic(self) -> None:
        """날짜 필터링 로직 검증"""
        url = reverse("admin-withdrawal-reasons-counts")
        today_str = self.now.strftime("%Y-%m-%d")

        response = self.client.get(url, {"from_date": today_str, "to_date": today_str})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["items"][0]["reason"], WithdrawalReason.OTHER)

    def test_get_withdrawal_reason_counts_success(self) -> None:
        """전체 기간 조회 검증"""
        url = reverse("admin-withdrawal-reasons-counts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 3)

        first_item = response.data["items"][0]
        self.assertEqual(first_item["reason"], WithdrawalReason.TECHNICAL_ISSUES)
        self.assertEqual(first_item["count"], 2)
        self.assertEqual(first_item["percentage"], 66.67)

    def test_get_monthly_withdrawal_stats_success(self) -> None:
        """월별 추세 API 성공 테스트"""
        url = reverse("admin-withdrawal-reasons-monthly-stats")
        reason_code = WithdrawalReason.TECHNICAL_ISSUES
        response = self.client.get(url, {"reason": reason_code})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reason"], reason_code)
        self.assertEqual(response.data["total"], 2)

    def test_monthly_stats_no_reason_returns_400(self) -> None:
        """필수 파라미터 누락 시 400 에러 검증"""
        url = reverse("admin-withdrawal-reasons-monthly-stats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
