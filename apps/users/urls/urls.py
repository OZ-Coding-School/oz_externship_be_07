from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views.admin_user_search_views import StudentManagementViewSet

router = DefaultRouter()

router.register("", StudentManagementViewSet, basename="admin-students")

urlpatterns = [
    path("", include(router.urls)),
]
from django.urls import path

from apps.users.views.send_email_views import EmailSendView
from apps.users.views.signup_views import SignUpView

app_name = "users"

urlpatterns = [
    path("signup", SignUpView.as_view(), name="signup"),
    path("email/send/", EmailSendView.as_view(), name="email-send"),
]
