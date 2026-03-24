from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.choices import UserRole, UserStatus, WithdrawalReason

# 3. User 직접 import (mypy 타입 인정을 위해)
from apps.users.models.models import User, Withdrawal


class AdminUserWithdrawalRestoreTest(TestCase):
    # 2. 클래스 레벨 타입 어노테이션 필수
    admin_user: User
    target_user: User
    withdrawal: Withdrawal
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        # 관리자 유저 생성
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            name="Empty",
            nickname="Random",
            phone_number="01011112222",
            birthday="19900101",
            role=UserRole.ADMIN,
            is_staff=True,
        )

        # 탈퇴 대기 유저 생성
        cls.target_user = User.objects.create_user(
            email="user@example.com",
            name="이제",
            nickname="이름어떻게짓지",
            phone_number="01033334444",
            birthday="19950505",
            status=UserStatus.WITHDREW,
            is_active=False,
        )

        # 탈퇴 정보 생성
        cls.withdrawal = Withdrawal.objects.create(
            user=cls.target_user, reason=WithdrawalReason.OTHER, reason_detail="개인 사정", due_date="2026-04-24"
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_restore_withdrawal_success_200(self) -> None:
        """성공: 어드민이 탈퇴 취소를 정상적으로 처리"""
        self.client.force_authenticate(user=self.admin_user)

        url = f"/api/v1/admin/withdrawals/{self.withdrawal.id}/"

        response = self.client.delete(url)

        # 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["error_detail"], "회원 탈퇴 취소처리 완료.")

        # DB 상태 검증
        self.assertFalse(Withdrawal.objects.filter(id=self.withdrawal.id).exists())

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.status, UserStatus.ACTIVATED)
        self.assertTrue(self.target_user.is_active)

    def test_restore_withdrawal_fail_404(self) -> None:
        """실패: 존재하지 않는 탈퇴 ID 요청"""
        self.client.force_authenticate(user=self.admin_user)

        # 존재할 수 없는 ID 사용
        invalid_id = 999999
        url = f"/api/v1/admin/withdrawals/{invalid_id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "회원탈퇴 정보를 찾을 수 없습니다.")

    def test_restore_withdrawal_fail_401_unauthorized(self) -> None:
        """실패: 인증되지 않은 사용자의 접근"""
        # 인증 없이 요청
        url = f"/api/v1/admin/withdrawals/{self.withdrawal.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")
