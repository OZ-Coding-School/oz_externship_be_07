from django.urls import path

from apps.community.views.comment_tagged_user_view import UserSearchAPIView

urlpatterns = [
    path("/search", UserSearchAPIView.as_view(), name="user-search"),
]
