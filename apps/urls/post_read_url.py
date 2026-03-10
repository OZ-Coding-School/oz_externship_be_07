from django.urls import path

from apps.community.views.post_list_view import PostListAPIView
from apps.community.views.post_detail_view import PostDetailAPIView
from apps.community.views.post_like_view import PostLikeAPIView

urlpatterns = [
    path("posts/", PostListAPIView.as_view(), name="post-list"),
    path("posts/<int:post_id>/", PostDetailAPIView.as_view(), name="post-detail"),
    path("posts/<int:post_id>/like/", PostLikeAPIView.as_view(), name="post-like"),
]