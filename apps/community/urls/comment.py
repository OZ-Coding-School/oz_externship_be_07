from django.urls import include, path

from apps.community.views.comment_views import CommentViewSet

urlpatterns = [
    path("", CommentViewSet.as_view({"get": "list", "post": "create"})),
    path("/<int:comment_id>", CommentViewSet.as_view({"put": "update", "delete": "destroy"})),
]
