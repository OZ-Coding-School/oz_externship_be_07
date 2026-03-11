from django.urls import include, path

urlpatterns = [
    path("<int:post_id>/comments", include("apps.community.urls.comment")),
    path("", include("apps.community.urls.post_category_url")),
]
