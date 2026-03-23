from django.urls import path

from apps.subject.views.cohort_student_views import (
    StudentListAPIView,
    StudentScoreAPIView,
)

urlpatterns = [
    path("admin/students", StudentListAPIView.as_view(), name="student-list"),
    path(
        "admin/students/<int:student_id>/scores",
        StudentScoreAPIView.as_view(),
        name="student-score",
    ),

]