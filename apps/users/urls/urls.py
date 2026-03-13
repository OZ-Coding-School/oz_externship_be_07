from django.urls import path

from apps.users.views.send_email_views import EmailSendView
from apps.users.views.signup_views import SignUpView
from apps.users.views.verify_email_views import EmailVerifyView

app_name = "users"

urlpatterns = [
    path("signup", SignUpView.as_view(), name="signup"),
    path("email/send/", EmailSendView.as_view(), name="email-send"),
    path("email/verify/", EmailVerifyView.as_view(), name="email-verify"),
]
