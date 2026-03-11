from django.urls import path

from apps.community.views.category_view import PostCategoryListSpecAPIView

urlpatterns = [
    path("categories", PostCategoryListSpecAPIView.as_view(), name="post-category-list"),
]
