from django.urls import path

from apps.subject.views.course_views import CourseListAPIView
from apps.subject.views.subject_views import (
    SubjectListCreateAPIView,
    SubjectScatterAPIView,
)

urlpatterns = [
    path(
        "<int:course_id>/subjects",
        SubjectListCreateAPIView.as_view(),
        name="subject-list-create",
    ),
    path(
        "admin/subjects/<int:subject_id>/scatter",
        SubjectScatterAPIView.as_view(),
        name="subject-scatter",
    ),
    path(
        "course",
        CourseListAPIView.as_view(),
        name="course-list",
    ),
]
