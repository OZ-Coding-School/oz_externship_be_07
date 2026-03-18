from django.urls import path

from apps.subject.views.cohort_admin_command_views import (
    AdminCohortCreateAPIView,
    AdminCohortUpdateAPIView,
)
from apps.subject.views.cohort_admin_query_views import (
    AdminCohortStudentListAPIView,
    AdminCourseCohortAvgScoresAPIView,
)
from apps.subject.views.cohort_views import CohortListAPIView

urlpatterns = [
    path("admin/cohorts", AdminCohortCreateAPIView.as_view()),
    path("<int:course_id>/cohorts", CohortListAPIView.as_view()),
    path("admin/cohorts/<int:cohort_id>", AdminCohortUpdateAPIView.as_view()),
    path("admin/courses/<int:course_id>/cohorts/avg-scores", AdminCourseCohortAvgScoresAPIView.as_view()),
    path("admin/cohorts/<int:cohort_id>/students", AdminCohortStudentListAPIView.as_view()),
]
