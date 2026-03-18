from django.urls import path

from apps.users.views.login_views import LoginView
from apps.users.views.send_email_views import EmailSendView
from apps.users.views.send_sms_views import SmsSendView
from apps.users.views.signup_views import SignUpView
from apps.users.views.verify_email_views import EmailVerifyView
from apps.users.views.verify_sms_views import SmsVerifyView

app_name = "users"

urlpatterns = [
    path("signup", SignUpView.as_view(), name="signup"),
    path("email/send/", EmailSendView.as_view(), name="email-send"),
    path("email/verify/", EmailVerifyView.as_view(), name="email-verify"),
    path("sms/send/", SmsSendView.as_view(), name="sms-send"),
    path("sms/verify/", SmsVerifyView.as_view(), name="sms-verify"),
    path("login/", LoginView.as_view(), name="login"),
]
