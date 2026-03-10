from django.db import models


# 성별
class UserGender(models.TextChoices):
    MALE = "M"
    FEMALE = "F"


# 소셜 종류
class SocialProvider(models.TextChoices):
    KAKAO = "kakao"
    NAVER = "naver"


# 유저 권한
class UserRole(models.TextChoices):
    USER = "USER"
    STUDENT = "STUDENT"
    TA = "TA"
    OM = "OM"
    LC = "LC"
    ADMIN = "ADMIN"


# 유저 상태
class UserStatus(models.TextChoices):
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"
    WITHDREW = "WITHDREW"


# 수강 진행 상황
class CohortStatus(models.TextChoices):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


# 수강신청 상태
class EnrollmentStatus(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"


# 분석 주기
class AnalyticsInterval(models.TextChoices):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


# 탈퇴 사유
class WithdrawalReason(models.TextChoices):
    GRADUATION = "GRADUATION", "졸업"
    TRANSFER = "TRANSFER", "전과/이직"
    NO_LONGER_NEEDED = "NO_LONGER_NEEDED", "더 이상 필요하지 않음"
    LACK_OF_INTEREST = "LACK_OF_INTEREST", "관심 부족"
    TOO_DIFFICULT = "TOO_DIFFICULT", "수업이 너무 어려움"
    FOUND_BETTER_SERVICE = "FOUND_BETTER_SERVICE", "더 나은 서비스 발견"
    PRIVACY_CONCERNS = "PRIVACY_CONCERNS", "개인정보 보안 우려"
    POOR_SERVICE_QUALITY = "POOR_SERVICE_QUALITY", "서비스 품질 불만족"
    TECHNICAL_ISSUES = "TECHNICAL_ISSUES", "기술적 문제"
    LACK_OF_CONTENT = "LACK_OF_CONTENT", "콘텐츠 부족"
    OTHER = "OTHER", "기타"
