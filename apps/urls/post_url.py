from django.urls import path
from apps.community.views import PostListCreateAPIView, PostDeleteAPIView

urlpatterns = [
    path("posts/", PostListCreateAPIView.as_view(), name="post-list-create"),
    path("posts/<int:post_id>/", PostDeleteAPIView.as_view(), name="post-delete"),
]