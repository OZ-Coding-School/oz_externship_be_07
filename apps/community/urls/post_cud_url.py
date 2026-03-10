from django.urls import path

from apps.community.views.post_cud_views import PostCreate, PostDetailUpdateDelete

urlpatterns = [
    path("", PostCreate.as_view(), name="post_create"),
    path("/<int:post_id>", PostDetailUpdateDelete.as_view(), name="post_detail_update_delete"),
]
