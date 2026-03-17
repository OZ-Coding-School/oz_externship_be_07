from django.urls import include, path

from apps.community.views.post_detail_view import PostDetailAPIView
from apps.community.views.post_list_view import PostListAPIView, FileUploadAPI

urlpatterns = [
    path("", PostListAPIView.as_view(), name="post-list"),
    path("<int:post_id>", PostDetailAPIView.as_view(), name="post-detail"),
    path("martor/", include("martor.urls")),
    path("file_upload", FileUploadAPI.as_view(), name="file-upload"),
]
