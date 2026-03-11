from django.urls import path

from apps.subject.views.cohort_views import (
    AdminCohortCreateAPIView,
    AdminCohortStudentListAPIView,
    AdminCohortUpdateAPIView,
    CohortListAPIView,
)
from apps.subject.views.subject_views import (
    AdminSubjectCreateAPIView,
    AdminSubjectListAPIView,
)

urlpatterns = [
    path("admin/subjects", AdminSubjectCreateAPIView.as_view(), name="subject-create"),
    path("<int:course_id>/subjects", AdminSubjectListAPIView.as_view(), name="subject-list"),
    path("admin/cohorts", AdminCohortCreateAPIView.as_view(), name="admin-cohort-create"),
    path("<int:course_id>/cohorts", CohortListAPIView.as_view(), name="cohort-list"),
    path("admin/cohorts/<int:cohort_id>", AdminCohortUpdateAPIView.as_view(), name="admin-cohort-update"),
    path(
        "admin/cohorts/<int:cohort_id>/students",
        AdminCohortStudentListAPIView.as_view(),
        name="admin-cohort-student-list",
    ),
]
