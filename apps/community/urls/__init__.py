from django.urls import include, path

urlpatterns = [
    path("", include("apps.community.urls.post_read_url")),
    path("", include("apps.community.urls.post_category_url")),
    path("<int:post_id>/comments", include("apps.community.urls.comment")),
]
