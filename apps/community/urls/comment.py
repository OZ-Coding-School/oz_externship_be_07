from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.community.views.comment_views import CommentViewSet

router = DefaultRouter()
router.register(r"", CommentViewSet, basename="post-comment")

urlpatterns = [
    path("", include(router.urls)),
]
