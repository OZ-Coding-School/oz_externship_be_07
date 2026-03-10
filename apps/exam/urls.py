from django.urls import path
from apps.exam import views

urlpatterns = [
    path("admin/exams", views.ExamListCreateAPIView.as_view(), name="exam-list-create"),
    path("admin/exams/<int:exam_id>", views.ExamDetailAPIView.as_view(), name="exam-detail"),
]
