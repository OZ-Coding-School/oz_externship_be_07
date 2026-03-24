from django.urls import include, path

urlpatterns = [
    path("", include("apps.community.urls.post_url")),
    path("/", include("apps.community.urls.post_category_url")),
    path("/user", include("apps.community.urls.user_search")),
    path("/<int:post_id>/comments", include("apps.community.urls.comment")),
]
