from django.urls import path, include

from apps.community.views import MartorTestVIew
from apps.community.views.post_detail_view import PostDetailAPIView
from apps.community.views.post_list_view import PostListAPIView

urlpatterns = [
    path("", PostListAPIView.as_view(), name="post-list"),
    path("<int:post_id>", PostDetailAPIView.as_view(), name="post-detail"),
    path('martor/', include('martor.urls')),
    path('martor-test', MartorTestVIew.as_view(), name="martor-test"),
]
