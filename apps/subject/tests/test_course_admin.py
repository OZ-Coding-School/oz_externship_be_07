from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.subject.models.course_models import Course
from apps.users.models.models import User


class CourseAdminAPITest(APITestCase):
    staff_user: User
    student_user: User
    course: Course
    create_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        """테스트 전체에서 사용할 기본 데이터 설정"""
        user_manager: Any = User.objects

        cls.staff_user = user_manager.create(
            email="admin@example.com",
            nickname="tadmin",
            name="관리자",
            role="ADMIN",
            status="ACTIVATED",
            birthday="1990-01-01",
            phone_number="01000000000",
        )

        cls.student_user = user_manager.create(
            email="student@example.com",
            nickname="tstudent",
            name="홍길동",
            role="STUDENT",
            status="ACTIVATED",
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        cls.course = Course.objects.create(
            name="기존과정",
            tag="EXT",
            description="기존 과정 설명",
            thumbnail_img_url="amazonaws.com/test_img_url",
        )

        cls.create_url = reverse("course-admin-create")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.staff_user))

    def _get_detail_url(self, course_id: int) -> str:
        return reverse("course-admin-update-delete", kwargs={"course_id": course_id})

    def test_create_course_success(self) -> None:
        """과정 등록 성공 테스트 (POST)"""
        data = {
            "name": "초격차 백엔드 부트캠프",
            "tag": "BE",
            "description": "백엔드 개발자 양성 과정",
            "thumbnail_img_url": "https://example.com/images/courses/backend.png",
        }
        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "과정이 등록되었습니다.")
        self.assertIn("id", response.data)
        self.assertTrue(Course.objects.filter(name="초격차 백엔드 부트캠프").exists())

    def test_create_course_missing_name_bad_request(self) -> None:
        """과정 등록 400 에러 : 필수 필드(name) 누락 시 실패 테스트"""
        data = {
            "tag": "BE",
        }
        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertIn("name", response.data["error_detail"])

    def test_create_course_missing_tag_bad_request(self) -> None:
        """과정 등록 400 에러 : 필수 필드(tag) 누락 시 실패 테스트"""
        data = {
            "name": "새과정",
        }
        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertIn("tag", response.data["error_detail"])

    def test_create_course_unauthorized_denied(self) -> None:
        """과정 등록 401 에러코드 테스트"""
        self.client.force_authenticate(user=None)
        data = {"name": "새과정", "tag": "NEW"}

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_create_course_permission_denied(self) -> None:
        """과정 등록 403 에러코드 테스트"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student_user))
        data = {"name": "새과정", "tag": "NEW"}

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_update_course_success(self) -> None:
        """과정 수정 성공 테스트 (PATCH)"""
        course = Course.objects.create(name="수정전과정", tag="BFR")
        url = reverse("course-admin-put-delete", kwargs={"course_id": course.pk})
        data = {"name": "수정후과정", "tag": "AFT"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "수정후과정")
        self.assertEqual(response.data["tag"], "AFT")
        self.assertIn("id", response.data)
        self.assertIn("updated_at", response.data)

    def test_update_course_partial_success(self) -> None:
        """과정 수정 성공 테스트 - 일부 필드만 수정 (PATCH)"""
        course = Course.objects.create(name="부분수정과정", tag="PRT")
        url = reverse("course-admin-put-delete", kwargs={"course_id": course.pk})
        data = {"description": "수정된 설명"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "수정된 설명")
        self.assertEqual(response.data["name"], "부분수정과정")

    def test_update_course_longer_then_3_characters_tag_bad_request(self) -> None:
        """과정 수정 400 에러 : tag length > 3"""
        course = Course.objects.create(name="수정대상과정2", tag="TG2")
        url = reverse("course-admin-put-delete", kwargs={"course_id": course.pk})
        data = {"tag": "EXIT"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertIn("tag", response.data["error_detail"])

    def test_update_course_unauthorized_denied(self) -> None:
        """과정 수정 401 에러코드 테스트"""
        url = reverse("course-admin-put-delete", kwargs={"course_id": self.course.pk})
        data = {"name": "수정시도"}

        self.client.force_authenticate(user=None)

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_update_course_permission_denied(self) -> None:
        """과정 수정 403 에러코드 테스트"""
        url = reverse("course-admin-put-delete", kwargs={"course_id": self.course.pk})
        data = {"name": "수정시도"}

        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student_user))

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_update_course_not_found(self) -> None:
        """과정 수정 404 에러코드 테스트"""
        url = reverse("course-admin-put-delete", kwargs={"course_id": 9999})
        data = {"name": "수정시도"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "과정을 찾을 수 없습니다.")

    def test_delete_course_success(self) -> None:
        """과정 삭제 성공 테스트 (DELETE)"""
        course = Course.objects.create(name="삭제대상과정", tag="DEL")
        url = reverse("course-admin-put-delete", kwargs={"course_id": course.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "과정이 삭제되었습니다.")
        self.assertFalse(Course.objects.filter(pk=course.pk).exists())

    def test_delete_course_unauthorized_denied(self) -> None:
        """과정 삭제 401 에러코드 테스트"""
        url = reverse("course-admin-put-delete", kwargs={"course_id": self.course.pk})
        self.client.force_authenticate(user=None)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_delete_course_permission_denied(self) -> None:
        """과정 삭제 403 에러코드 테스트"""
        url = reverse("course-admin-put-delete", kwargs={"course_id": self.course.pk})
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student_user))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_delete_course_not_found(self) -> None:
        """과정 삭제 404 에러코드 테스트"""
        url = reverse("course-admin-put-delete", kwargs={"course_id": 9999})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "과정을 찾을 수 없습니다.")
