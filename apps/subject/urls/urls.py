from django.urls import path

from apps.subject.views.subject_views import (
    SubjectListCreateAPIView,
    SubjectScatterAPIView,
)

urlpatterns = [
    path(
        "api/v1/<int:course_id>/subjects",
        SubjectListCreateAPIView.as_view(),
        name="subject-list-create",
    ),
    path(
        "api/v1/admin/subjects/<int:subject_id>/scatter",
        SubjectScatterAPIView.as_view(),
        name="subject-scatter",
    ),
]