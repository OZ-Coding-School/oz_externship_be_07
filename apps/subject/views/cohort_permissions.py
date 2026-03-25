from apps.core.permissions import IsStaffUser

class IsSubjectStaffUser(IsStaffUser):
    message = "권한이 없습니다."

class CanViewCohortList(IsSubjectStaffUser):
    message = "이 리소스를 조회할 권한이 없습니다."