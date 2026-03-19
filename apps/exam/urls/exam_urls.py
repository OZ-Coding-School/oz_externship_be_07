from django.urls import path

from apps.exam.views import exam_crud_views

urlpatterns = [
    path("admin/exams", exam_crud_views.ExamListCreateAPIView.as_view(), name="exam-list-create"),
    path("admin/exams/<int:exam_id>", exam_crud_views.ExamDetailAPIView.as_view(), name="exam-detail"),
]
