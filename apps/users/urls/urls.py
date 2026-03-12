from django.urls import path

from apps.users.views.send_email_views import EmailSendView
from apps.users.views.signup_views import SignUpView

app_name = "users"

urlpatterns = [
    path("signup", SignUpView.as_view(), name="signup"),
    path("email/send/", EmailSendView.as_view(), name="email-send"),
]
