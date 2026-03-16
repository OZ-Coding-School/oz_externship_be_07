from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views.admin.user_enrollment import AdminUserEnrollmentViewSet
from apps.users.views.admin.user_search import StudentManagementViewSet

router = DefaultRouter()
router.register(r"students", StudentManagementViewSet, basename="admin-students")
router.register(r"student-enrollments", AdminUserEnrollmentViewSet, basename="admin-enrollments")

urlpatterns = [
    path("", include(router.urls)),
]
