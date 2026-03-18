from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views.admin.user_enrollment import AdminUserEnrollmentViewSet
from apps.users.views.admin.user_enrollment_accept import AdminEnrollmentAcceptAPIView
from apps.users.views.admin.user_enrollment_reject import AdminEnrollmentRejectAPIView
from apps.users.views.admin.user_role_change import AdminUserRoleUpdateAPIView
from apps.users.views.admin.user_search import StudentManagementViewSet

router = DefaultRouter()
router.register(r"students", StudentManagementViewSet, basename="admin-students")
router.register(r"student-enrollments", AdminUserEnrollmentViewSet, basename="admin-enrollments")

urlpatterns = [
    path("student-enrollments/accept/", AdminEnrollmentAcceptAPIView.as_view(), name="admin-enrollment-accept"),
    path("student-enrollments/reject/", AdminEnrollmentRejectAPIView.as_view(), name="admin-enrollment-reject"),
    path("accounts/<int:account_id>/role/", AdminUserRoleUpdateAPIView.as_view(), name="admin-user-role-update"),
    path("", include(router.urls)),
]
