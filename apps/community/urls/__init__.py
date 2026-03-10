from django.urls import include, path

urlpatterns = [
    path("/<int:post_id>/comments", include("apps.community.urls.comment")),
]
