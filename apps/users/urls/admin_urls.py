from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views.admin.user_analytics import (
    AdminSignupTrendAPIView,
    AdminWithdrawalTrendAPIView,
)
from apps.users.views.admin.user_enrollment import AdminUserEnrollmentViewSet
from apps.users.views.admin.user_enrollment_accept import AdminEnrollmentAcceptAPIView
from apps.users.views.admin.user_enrollment_reject import AdminEnrollmentRejectAPIView
from apps.users.views.admin.user_enrollment_trend_analytics import (
    AdminStudentEnrollmentTrendAPIView,
)
from apps.users.views.admin.user_management import AdminUserDeleteAPIView
from apps.users.views.admin.user_role_change import AdminUserRoleUpdateAPIView
from apps.users.views.admin.user_search import StudentManagementViewSet
from apps.users.views.admin.user_withdrawal_analytics import (
    WithdrawalMonthlyReasonStatsAPIView,
    WithdrawalReasonCountAPIView,
)
from apps.users.views.admin.user_withdrawal_list import AdminUserWithdrawalAPIView

router = DefaultRouter()
router.register(r"students", StudentManagementViewSet, basename="admin-students")
router.register(r"student-enrollments", AdminUserEnrollmentViewSet, basename="admin-enrollments")

urlpatterns = [
    path("student-enrollments/accept/", AdminEnrollmentAcceptAPIView.as_view(), name="admin-enrollment-accept"),
    path("student-enrollments/reject/", AdminEnrollmentRejectAPIView.as_view(), name="admin-enrollment-reject"),
    path("accounts/<int:account_id>/", AdminUserDeleteAPIView.as_view(), name="admin-user-delete"),
    path("accounts/<int:account_id>/role/", AdminUserRoleUpdateAPIView.as_view(), name="admin-user-role-update"),
    path("withdrawals/", AdminUserWithdrawalAPIView.as_view(), name="admin-withdrawal-list"),
    path("withdrawals/<int:withdrawal_id>/", AdminUserWithdrawalAPIView.as_view(), name="admin-withdrawal-detail"),
    path("analytics/signup/trends/", AdminSignupTrendAPIView.as_view(), name="admin-signup-trend"),
    path("analytics/withdrawals/trends/", AdminWithdrawalTrendAPIView.as_view(), name="admin-withdrawal-trend"),
    path(
        "analytics/withdrawal-reasons/counts/",
        WithdrawalReasonCountAPIView.as_view(),
        name="admin-withdrawal-reasons-counts",
    ),
    path(
        "analytics/withdrawal-reasons/stats/monthly/",
        WithdrawalMonthlyReasonStatsAPIView.as_view(),
        name="admin-withdrawal-reasons-monthly-stats",
    ),
    path(
        "student-enrollments/trends/",
        AdminStudentEnrollmentTrendAPIView.as_view(),
        name="admin-student-enrollment-trends",
    ),
    path("", include(router.urls)),
]
