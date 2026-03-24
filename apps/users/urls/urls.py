from django.urls import path

from apps.users.views.available_courses import AvailableCourseListAPIView
from apps.users.views.change_phone_views import ChangePhoneNumberView
from apps.users.views.enroll_student import EnrollStudentAPIView
from apps.users.views.find_email_views import FindEmailView
from apps.users.views.login_views import LoginView
from apps.users.views.logout_views import LogoutView
from apps.users.views.profile_views import (
    NicknameCheckView,
    ProfileImageView,
    ProfileView,
)
from apps.users.views.re_token_views import ReTokenView
from apps.users.views.send_email_views import EmailSendView
from apps.users.views.send_sms_views import SmsSendView
from apps.users.views.signup_views import SignUpView
from apps.users.views.social_login_views import (
    KakaoLoginCallbackView,
    KakaoLoginStartView,
    NaverLoginCallbackView,
    NaverLoginStartView,
)
from apps.users.views.verify_email_views import EmailVerifyView
from apps.users.views.verify_sms_views import SmsVerifyView

app_name = "users"

urlpatterns = [
    path("signup", SignUpView.as_view(), name="signup"),
    path("verification/send-email", EmailSendView.as_view(), name="email-send"),
    path("verification/verify-email", EmailVerifyView.as_view(), name="email-verify"),
    path("verification/send-sms", SmsSendView.as_view(), name="sms-send"),
    path("verification/verify-sms", SmsVerifyView.as_view(), name="sms-verify"),
    path("login", LoginView.as_view(), name="login"),
    path("me/refresh", ReTokenView.as_view(), name="token-refresh"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("social-login/kakao", KakaoLoginStartView.as_view(), name="kakao-start"),
    path("social-login/kakao/callback", KakaoLoginCallbackView.as_view(), name="kakao-callback"),
    path("social-login/naver", NaverLoginStartView.as_view(), name="naver-start"),
    path("social-login/naver/callback", NaverLoginCallbackView.as_view(), name="naver-callback"),
    path("find-email/", FindEmailView.as_view(), name="find-email"),
    path("enroll-student/", EnrollStudentAPIView.as_view(), name="enroll-student"),
    path("available-courses/", AvailableCourseListAPIView.as_view(), name="available-courses"),
    path("find-email", FindEmailView.as_view(), name="find-email"),
    path("enroll-student", EnrollStudentAPIView.as_view(), name="enroll-student"),
    path("available-courses", AvailableCourseListAPIView.as_view(), name="available-courses"),
    path("me", ProfileView.as_view(), name="profile"),
    path("check-nickname", NicknameCheckView.as_view(), name="check-nickname"),
    path("me/profile-image", ProfileImageView.as_view(), name="profile-image"),
    path("change-phone", ChangePhoneNumberView.as_view(), name="change-phone"),
]
