from typing import Any

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.subject.models.choices import SubjectStatus
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject


class SubjectAPITest(APITestCase):
    """Subject API 테스트"""

    course: Course
    subject: Subject
    subject_data: dict[str, Any]
    list_create_url: str
    scatter_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        """테스트 전체에서 공통으로 사용할 데이터 생성"""

        cls.course = Course.objects.create(
            name="testcourse",
            tag="tst",
            description="test",
            thumbnail_img_url="amazonaws.com/test_img_url",
        )

        cls.subject = Subject.objects.create(
            course=cls.course,
            title="testsubject",
            number_of_days=5,
            number_of_hours=40,
            thumbnail_img_url="amazonaws.com/test_img_url",
            status=SubjectStatus.ACTIVATED,
        )

        cls.subject_data = {
            "course_id": cls.course.pk,
            "title": "testsubject",
            "number_of_days": 5,
            "number_of_hours": 40,
            "thumbnail_img_url": "amazonaws.com/test_img_url",
        }

        cls.list_create_url = reverse(
            "subject-list-create",
            kwargs={"course_id": cls.course.pk},
        )

        cls.scatter_url = reverse(
            "subject-scatter",
            kwargs={"subject_id": cls.subject.pk},
        )

    def test_create_subject_success(self) -> None:
        """과목 생성 성공 테스트"""

        data = self.subject_data.copy()
        data["title"] = "subject_test"
        data["number_of_days"] = 7
        data["thumbnail_img_url"] = "oz_test/test_img_url"

        response = self.client.post(self.list_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Subject.objects.count(), 2)

        self.assertEqual(response.data["title"], "subject_test")
        self.assertEqual(response.data["number_of_days"], 7)
        self.assertEqual(response.data["thumbnail_img_url"], "oz_test/test_img_url")

    def test_create_subject_fail_missing_title(self) -> None:
        """과목 생성 실패 테스트 - title 누락"""

        data = self.subject_data.copy()
        data.pop("title")

        response = self.client.post(self.list_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_subject_fail_missing_course_id(self) -> None:
        """과목 생성 실패 테스트 - course_id 누락"""

        data = self.subject_data.copy()
        data.pop("course_id")

        response = self.client.post(self.list_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_subject_list_success(self) -> None:
        """과목 목록 조회 성공 테스트"""

        for i in range(10):
            Subject.objects.create(
                course=self.course,
                title=f"subject {i}",
                number_of_days=5,
                number_of_hours=40,
                thumbnail_img_url="amazonaws.com/test",
                status=SubjectStatus.ACTIVATED,
            )

        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(len(response.data) >= 1)

    def test_get_subject_list_contains_created_subject(self) -> None:
        """과목 목록 조회 테스트 - 미리 생성한 과목이 포함되는지 확인"""

        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, list):
            titles = [item["title"] for item in response.data]
        else:
            results = response.data.get("results", [])
            titles = [item["title"] for item in results]

        self.assertIn("testsubject", titles)

    def test_get_subject_scatter_success(self) -> None:
        """과목 산점도 조회 성공 테스트"""

        response = self.client.get(self.scatter_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_subject_scatter_not_found(self) -> None:
        """과목 산점도 조회 실패 테스트 - 존재하지 않는 subject_id"""

        url = reverse("subject-scatter", kwargs={"subject_id": 9999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)