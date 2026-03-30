from django.urls import path

from apps.users.views.account_recovery_views import AccountRecoveryView
from apps.users.views.auth_views import LoginView, LogoutView, ReTokenView, SignUpView
from apps.users.views.available_courses import AvailableCourseListAPIView
from apps.users.views.change_password_views import PasswordChangeView
from apps.users.views.change_phone_views import ChangePhoneNumberView
from apps.users.views.enroll_student import EnrollStudentAPIView
from apps.users.views.find_email_views import FindEmailView
from apps.users.views.find_password_views import PasswordFindView
from apps.users.views.mycourse_check_views import MyEnrolledCourseView
from apps.users.views.profile_presigned_url_view import ProfilePresignedUrlView
from apps.users.views.profile_views import (
    NicknameCheckView,
    ProfileImageView,
    ProfileView,
)
from apps.users.views.social_login_views import (
    KakaoLoginCallbackView,
    KakaoLoginStartView,
    NaverLoginCallbackView,
    NaverLoginStartView,
)
from apps.users.views.verification_views import (
    EmailSendView,
    EmailVerifyView,
    SmsSendView,
    SmsVerifyView,
)

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
    path("find-email", FindEmailView.as_view(), name="find-email"),
    path("enroll-student", EnrollStudentAPIView.as_view(), name="enroll-student"),
    path("available-courses", AvailableCourseListAPIView.as_view(), name="available-courses"),
    path("me", ProfileView.as_view(), name="profile"),
    path("check-nickname", NicknameCheckView.as_view(), name="check-nickname"),
    path("me/profile-image", ProfileImageView.as_view(), name="profile-image"),
    path("me/profile-image/presigned-url", ProfilePresignedUrlView.as_view(), name="profile-presigned-url"),
    path("change-phone", ChangePhoneNumberView.as_view(), name="change-phone"),
    path("me/enrolled-courses", MyEnrolledCourseView.as_view(), name="me-enrolled-courses"),
    path("change-password", PasswordChangeView.as_view(), name="change-password"),
    path("restore", AccountRecoveryView.as_view(), name="restore"),
    path("find-password", PasswordFindView.as_view(), name="find-password"),
]
