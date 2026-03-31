from datetime import timedelta
from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.course_models import Course
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.subject.models.operation_manager_models import OperationManager
from apps.subject.models.traning_assistant_models import TrainingAssistant
from apps.users.choices import EnrollmentStatus, UserRole, UserStatus
from apps.users.models.models import User


# =========================
# Base Test Case
# =========================
class AdminUserDeleteTest(TestCase):
    admin_user: User
    regular_user: User
    target_user: User
    client: APIClient
    base_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.base_url = "/api/v1/admin/accounts/"
        user_manager: Any = User.objects

        # 관리자 생성
        cls.admin_user = user_manager.create(
            email="admin@example.com",
            nickname="집이지만",
            name="admin",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVATED,
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.admin_user.is_staff = True
        cls.admin_user.save()

        # 일반 유저 생성
        cls.target_user = user_manager.create(
            email="user@example.com",
            nickname="집가고싶다",
            name="user",
            role=UserRole.USER,
            status=UserStatus.ACTIVATED,
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        # 삭제 대상 유저 생성
        cls.regular_user = user_manager.create(
            email="target@example.com",
            nickname="너무나",
            name="쉬고싶다",
            role=UserRole.USER,
            status=UserStatus.ACTIVATED,
            birthday="1990-01-01",
            phone_number="01000000002",
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_delete_user_success_200(self) -> None:
        """200 OK: 어드민이 유저를 성공적으로 삭제하는 경우"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))
        url = f"{self.base_url}{self.target_user.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], f"유저 데이터가 삭제되었습니다. - pk: {self.target_user.id}")
        # DB에서 실제로 삭제되었는지 확인
        self.assertFalse(User.objects.filter(id=self.target_user.id).exists())

    def test_delete_user_fail_401_unauthorized(self) -> None:
        """401 Unauthorized: 인증 데이터가 없는 경우"""
        url = f"{self.base_url}{self.target_user.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_delete_user_fail_403_forbidden(self) -> None:
        """403 Forbidden: 관리자 권한이 없는 유저가 삭제를 시도하는 경우"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.regular_user))
        url = f"{self.base_url}{self.target_user.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], "권한이 없습니다.")

    def test_delete_user_fail_404_not_found(self) -> None:
        """404 Not Found: 존재하지 않는 유저 ID를 삭제하려는 경우"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))
        invalid_url = f"{self.base_url}9999/"  # 존재하지 않는 ID

        response = self.client.delete(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "사용자 정보를 찾을 수 없습니다.")


class EnrollStudentTest(TestCase):
    client: APIClient
    user: User
    cohort: Cohort
    course: Course
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/accounts/enroll-student"
        cls.course = Course.objects.create(name="Python 백엔드 과정")

        # 테스트 유저 생성
        cls.user = User.objects.create(
            email="student@example.com",
            nickname="뽀로로와",
            name="친구들",
            phone_number="01012345678",
            birthday="2000-01-01",
            role=UserRole.USER,
            status=UserStatus.ACTIVATED,
        )

        # 테스트 기수 생성
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=3,
            max_student=30,
            start_date="2026-03-01",
            end_date="2026-06-01",
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_enroll_student_success_201(self) -> None:
        """201 Created: 정상적인 기수 등록 신청"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))

        data: dict[str, Any] = {"cohort_id": self.cohort.id}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(EnrollmentRequest.objects.filter(user=self.user, cohort=self.cohort).exists())
        self.assertFalse(CohortStudent.objects.filter(user=self.user, cohort=self.cohort).exists())

    def test_enroll_student_fail_already_pending(self) -> None:
        """400 Bad Request: 대기 중인 신청이 있을 때"""
        EnrollmentRequest.objects.create(user=self.user, cohort=self.cohort, status=EnrollmentStatus.PENDING)

        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))
        response = self.client.post(self.url, data={"cohort_id": self.cohort.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"]["detail"][0], "이미 신청한 기수입니다.")

    def test_enroll_student_fail_already_accepted(self) -> None:
        """400 Bad Request: 이미 승인된 신청(수강 중)이 있을 때"""
        EnrollmentRequest.objects.create(user=self.user, cohort=self.cohort, status=EnrollmentStatus.ACCEPTED)

        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))
        response = self.client.post(self.url, data={"cohort_id": self.cohort.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"]["detail"][0], "이미 등록된 기수입니다.")

    def test_enroll_student_fail_401_unauthorized(self) -> None:
        """401 Unauthorized: 로그인하지 않은 상태로 요청"""
        data = {"cohort_id": self.cohort.id}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")


class AdminUserRoleUpdateTest(TestCase):
    admin_user: User
    target_user: User
    cohort: Cohort
    course: Course
    client: APIClient
    url: str
    base_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.base_url = "/api/v1/admin/accounts/"
        user_manager: Any = User.objects

        # 관리자 생성
        cls.admin_user = user_manager.create(
            email="admin@example.com",
            nickname="admin97",
            name="관리자",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVATED,
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.admin_user.is_staff = True
        cls.admin_user.save()

        # 테스트 유저 생성
        cls.target_user = user_manager.create(
            email="user@example.com",
            nickname="user97",
            name="대상자",
            role=UserRole.USER,
            status=UserStatus.ACTIVATED,
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        # 강의 및 기수 생성
        cls.course = Course.objects.create(name="초격차 백엔드 부트캠프", tag="BE")

        now = timezone.now().date()
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=10,
            max_student=30,
            start_date=now,
            end_date=now + timedelta(days=90),
            status=EnrollmentStatus.PENDING,
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))
        self.url = f"{self.base_url}{self.target_user.id}/role/"

    def test_update_role_to_student_success(self) -> None:
        """수강생(STUDENT) 권한 변경 및 CohortStudent 생성 테스트"""
        data = {"role": UserRole.STUDENT, "cohort_id": self.cohort.id}
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, UserRole.STUDENT)

        self.assertTrue(CohortStudent.objects.filter(user=self.target_user, cohort_id=self.cohort.id).exists())

    def test_update_role_to_om_success(self) -> None:
        """운영매니저(OM) 권한 변경 테스트"""
        data = {"role": UserRole.OM, "assigned_courses": [self.course.id]}
        response = self.client.patch(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, UserRole.OM)
        self.assertTrue(OperationManager.objects.filter(user=self.target_user, course=self.course).exists())

    def test_update_role_to_ta_success(self) -> None:
        """조교(TA) 권한 변경 테스트"""
        data = {"role": UserRole.TA, "cohort_id": self.cohort.id}
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, UserRole.TA)

    def test_update_role_fail_400_bad_request(self) -> None:
        """조교(TA) 변경 시 기수 정보가 없는 경우"""
        data = {"role": UserRole.TA}
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cohort_id", response.json()["error_detail"])
        self.assertEqual(response.json()["error_detail"]["cohort_id"][0], "기수 정보가 필요합니다.")

    def test_update_role_fail_invalid_cohort_id(self) -> None:
        """존재하지 않는 기수 ID인 경우"""
        data = {"role": UserRole.STUDENT, "cohort_id": 99999}
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_detail"]["cohort_id"][0], "존재하지 않는 기수 ID입니다.")

    def test_update_role_to_lc_success(self) -> None:
        """운영진(LC) 권한 변경 성공 테스트"""
        data = {"role": UserRole.LC, "assigned_courses": [self.course.id]}
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, UserRole.LC)

    def test_update_role_lc_fail_missing_courses(self) -> None:
        """LC/OM 변경 시 코스 정보가 없는 경우"""
        data = {"role": UserRole.OM}  # assigned_courses 누락
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_detail"]["assigned_courses"][0], "코스 정보가 필요합니다.")

    def test_update_role_lc_fail_invalid_course_id(self) -> None:
        """존재하지 않는 코스 ID가 포함된 경우"""
        data = {"role": UserRole.LC, "assigned_courses": [self.course.id, 99999]}
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["error_detail"]["assigned_courses"][0], "존재하지 않는 코스 ID가 포함되어 있습니다."
        )

    def test_update_role_fail_401_unauthorized(self) -> None:
        """로그인을 하지 않고 접근하는 경우"""
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.url, data={"role": UserRole.STUDENT, "cohort_id": self.cohort.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_role_fail_403_forbidden(self) -> None:
        """관리자가 아닌 일반 유저가 권한 변경을 시도하는 경우"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))
        data = {"role": UserRole.TA, "cohort_id": self.cohort.id}
        response = self.client.patch(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_role_fail_404_not_found(self) -> None:
        """존재하지 않는 유저 ID로 요청하는 경우"""
        invalid_url = f"{self.base_url}9999/role/"
        data = {"role": UserRole.TA, "cohort_id": self.cohort.id}
        response = self.client.patch(invalid_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminUserEnrollmentTest(TestCase):
    admin_user: User
    target_user: User
    enrollment: EnrollmentRequest
    cohort: Cohort
    client: APIClient
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/admin/student-enrollments/"
        user_manager: Any = User.objects

        # 테스트 관리자 생성
        cls.admin_user = user_manager.create(
            email="admin@example.com",
            nickname="tadmin",
            name="관리자",
            role="ADMIN",
            status="ACTIVATED",
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.admin_user.is_staff = True
        cls.admin_user.save()

        # 테스트 유저 생성
        cls.target_user = user_manager.create(
            email="student@example.com",
            nickname="tstudent",
            name="홍길동",
            role="STUDENT",
            status="ACTIVATED",
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        course = Course.objects.create(name="초격차 백엔드 부트캠프", tag="BE")

        now = timezone.now().date()
        cls.cohort = Cohort.objects.create(
            course=course,
            number=10,
            max_student=30,
            start_date=now,
            end_date=now + timedelta(days=90),
            status="PENDING",
        )

        cls.enrollment = EnrollmentRequest.objects.create(user=cls.target_user, cohort=cls.cohort, status="PENDING")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_get_enrollment_list_success(self) -> None:
        """수강 신청 목록 조회 성공 테스트 (관리자 권한)"""
        params: dict[str, Any] = {"page": 1, "page_size": 10}
        response = self.client.get(self.url, data=params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["count"], 1)
        result = data["results"][0]
        self.assertEqual(result["id"], self.enrollment.id)
        self.assertEqual(result["user"]["id"], self.target_user.id)
        self.assertEqual(result["user"]["name"], "홍길동")

    def test_get_enrollment_list_unauthorized(self) -> None:
        """401 Unauthorized 테스트"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_enrollment_list_permission_denied(self) -> None:
        """403 Forbidden 테스트"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminEnrollmentAcceptTest(APITestCase):
    admin_user: User
    user: User
    course: Course
    cohort: Cohort
    enroll1: EnrollmentRequest
    enroll2: EnrollmentRequest
    already_approved: EnrollmentRequest
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        user_manager: Any = User.objects

        # 유저 생성
        cls.admin_user = user_manager.create_user(
            email="admin@example.com",
            password="password123",
            role="ADMIN",
            name="관리자",
            nickname="admin99",
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.user = user_manager.create_user(
            email="student@example.com",
            password="password123",
            role="USER",
            name="학생",
            nickname="student99",
            birthday="1995-05-05",
            phone_number="01012345678",
        )

        # 강의 및 기수 생성
        cls.course = Course.objects.create(name="백엔드 코스", tag="BE")
        now = timezone.now().date()
        cls.cohort = Cohort.objects.create(
            number=1,
            course=cls.course,
            max_student=30,
            start_date=now,
            end_date=now + timedelta(days=90),
            status="PENDING",
        )

        # 신청 데이터 생성
        cls.enroll1 = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="PENDING")
        cls.enroll2 = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="PENDING")
        cls.already_approved = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="ACCEPTED")

        cls.url = reverse("admin-enrollment-accept")

    def setUp(self) -> None:
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_accept_enrollments_success(self) -> None:
        """정상적인 승인 요청 테스트"""
        data: dict[str, list[int]] = {"enrollments": [self.enroll1.id, self.enroll2.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "2건의 수강 신청이 승인되었습니다.")

        # DB 반영 확인
        self.enroll1.refresh_from_db()
        self.enroll2.refresh_from_db()
        self.assertEqual(self.enroll1.status, "ACCEPTED")
        self.assertEqual(self.enroll2.status, "ACCEPTED")

    def test_accept_enrollments_empty_list(self) -> None:
        """빈 리스트 요청 시 시리얼라이저 에러 확인 (400)"""
        data: dict[str, list[Any]] = {"enrollments": []}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("enrollments", response.data["error_detail"])

    def test_accept_enrollments_fail_already_approved(self) -> None:
        """이미 승인된 건에 대해 요청 시 400 에러 확인"""
        data: dict[str, list[int]] = {"enrollments": [self.already_approved.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("승인 가능한 대기 상태의 신청 건이 없습니다.", str(response.data.get("error_detail", "")))

    def test_accept_enrollments_permission_denied(self) -> None:
        """일반 유저가 요청 시 403 에러 확인"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))

        data: dict[str, list[int]] = {"enrollments": [self.enroll1.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminEnrollmentRejectTest(APITestCase):
    admin_user: User
    user: User
    course: Course
    cohort: Cohort
    enroll1: EnrollmentRequest
    enroll2: EnrollmentRequest
    already_approved: EnrollmentRequest
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        user_manager: Any = User.objects

        # 유저 생성
        cls.admin_user = user_manager.create_user(
            email="admin@example.com",
            password="password123",
            role="ADMIN",
            name="관리자",
            nickname="admin98",
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.user = user_manager.create_user(
            email="student@example.com",
            password="password123",
            role="USER",
            name="학생",
            nickname="student98",
            birthday="1995-05-05",
            phone_number="01012345678",
        )

        # 강의 및 기수 생성
        cls.course = Course.objects.create(name="백엔드 코스", tag="BE")
        now = timezone.now().date()
        cls.cohort = Cohort.objects.create(
            number=1,
            course=cls.course,
            max_student=30,
            start_date=now,
            end_date=now + timedelta(days=90),
            status="PENDING",
        )

        # 신청 데이터 생성
        cls.enroll1 = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="PENDING")
        cls.enroll2 = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="PENDING")
        cls.already_approved = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="REJECTED")

        cls.url = reverse("admin-enrollment-reject")

    def setUp(self) -> None:
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_reject_enrollments_success(self) -> None:
        """정상적인 반려 요청 테스트"""
        data: dict[str, list[int]] = {"enrollments": [self.enroll1.id, self.enroll2.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "2건의 수강 신청이 반려되었습니다.")

        # DB 반영 확인
        self.enroll1.refresh_from_db()
        self.enroll2.refresh_from_db()
        self.assertEqual(self.enroll1.status, "REJECTED")
        self.assertEqual(self.enroll2.status, "REJECTED")

    def test_reject_enrollments_empty_list(self) -> None:
        """빈 리스트 요청 시 시리얼라이저 에러 확인 (400)"""
        data: dict[str, list[Any]] = {"enrollments": []}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("enrollments", response.data["error_detail"])

    def test_reject_enrollments_fail_already_approved(self) -> None:
        """이미 승인된 건에 대해 요청 시 400 에러 확인"""
        data: dict[str, list[int]] = {"enrollments": [self.already_approved.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("반려 가능한 대기 상태의 신청 건이 없습니다.", str(response.data.get("error_detail", "")))

    def test_reject_enrollments_permission_denied(self) -> None:
        """일반 유저가 요청 시 403 에러 확인"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))

        data: dict[str, list[int]] = {"enrollments": [self.enroll1.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
