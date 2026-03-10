from django.urls import path

from apps.community.views.post_views_crd import PostCreate, PostDetailUpdateDelete

urlpatterns = [
    path("", PostCreate.as_view(), name="post"),
    path("/<int:post_id>", PostDetailUpdateDelete.as_view(), name="post"),
]
