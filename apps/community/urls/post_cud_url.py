from django.urls import path

from apps.community.views.post_cud_views import PostCreate, PostDetailUpdateDelete

urlpatterns = [
    path("", PostCreate.as_view(), name="post"),
    path("/<int:post_id>", PostDetailUpdateDelete.as_view(), name="post"),
]
