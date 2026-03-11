from django.urls import path

from apps.community.views.post_detail_view import PostDetailAPIView
from apps.community.views.post_list_view import PostListAPIView

urlpatterns = [
    path("posts/", PostListAPIView.as_view(), name="post-list"),
    path("posts/<int:post_id>/", PostDetailAPIView.as_view(), name="post-detail"),
]