from __future__ import annotations

from datetime import date

from django.test import RequestFactory, TestCase

from apps.subject.views.cohort_permissions import CanViewCohortList, IsSubjectStaffUser
from apps.users.models.models import User


class CohortPermissionTests(TestCase):
    staff_user: User
    normal_user: User
    factory: RequestFactory

    @classmethod
    def setUpTestData(cls) -> None:
        cls.staff_user = User.objects.create_user(
            email="staff@example.com",
            password="1234",
            name="관리자",
            nickname="staffuser",
            phone_number="01012345678",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="ADMIN",
        )
        cls.normal_user = User.objects.create_user(
            email="user@example.com",
            password="1234",
            name="일반유저",
            nickname="normaluser",
            phone_number="01087654321",
            gender="FEMALE",
            birthday=date(2000, 1, 2),
            role="USER",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_is_subject_staff_user_returns_true_for_staff_role(self) -> None:
        request = self.factory.get("/api/v1/admin/cohorts")
        request.user = self.staff_user

        permitted = IsSubjectStaffUser().has_permission(request, view=None)  # type: ignore[arg-type]

        self.assertTrue(permitted)

    def test_is_subject_staff_user_returns_false_for_normal_user(self) -> None:
        request = self.factory.get("/api/v1/admin/cohorts")
        request.user = self.normal_user

        permitted = IsSubjectStaffUser().has_permission(request, view=None)  # type: ignore[arg-type]

        self.assertFalse(permitted)

    def test_can_view_cohort_list_returns_true_for_staff_role(self) -> None:
        request = self.factory.get("/api/v1/1/cohorts")
        request.user = self.staff_user

        permitted = CanViewCohortList().has_permission(request, view=None)  # type: ignore[arg-type]

        self.assertTrue(permitted)

    def test_can_view_cohort_list_returns_false_for_normal_user(self) -> None:
        request = self.factory.get("/api/v1/1/cohorts")
        request.user = self.normal_user

        permitted = CanViewCohortList().has_permission(request, view=None)  # type: ignore[arg-type]

        self.assertFalse(permitted)