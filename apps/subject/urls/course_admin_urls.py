from django.urls import path

from apps.subject.views.course_admin_views import (
    CourseAdminCreateAPIView,
    CourseAdminUpdateDeleteAPIView,
)

urlpatterns = [
    path("admin/courses", CourseAdminCreateAPIView.as_view(), name="course-admin-create"),
    path("admin/courses/<course_id>", CourseAdminUpdateDeleteAPIView.as_view(), name="course-admin-put-delete"),
]
