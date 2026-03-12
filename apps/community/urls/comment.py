from django.urls import path

from apps.community.views.comment_views import CommentViewSet

urlpatterns = [
    path("", CommentViewSet.as_view({"get": "list", "post": "create"}), name="post-comment-list"),
    path(
        "/<int:comment_id>", CommentViewSet.as_view({"put": "update", "delete": "destroy"}), name="post-comment-detail"
    ),
]
