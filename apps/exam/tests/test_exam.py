from typing import IO, Any, Dict

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.exam.models.exam_models import Exam
from apps.subject.models.choices import SubjectStatus
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject


class ExamAPITest(APITestCase):
    # 속성 타입 선언 (attr-defined 에러 해결)
    course: Course
    subject: Subject
    exam_data: Dict[str, Any]
    url: str

    @classmethod
    def setUpTestData(cls) -> None:  # 리턴 타입 명시
        """테스트 전체에서 사용할 기본 데이터 설정"""
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

        cls.exam_data = {
            "title": "testexam",
            "subject": cls.subject,
            "thumbnail_img": "amazonaws.com/test_img_url",
        }

        cls.url = reverse("exam-list-create")

    def test_create_exam_success(self) -> None:
        """쪽지시험 생성 성공 테스트 (POST)"""

        data = self.exam_data.copy()
        data["title"] = "testtest"
        data["subject"] = self.subject.pk
        data["thumbnail_img"] = "oz_test/test_img_url"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 1)
        self.assertEqual(response.data["title"], "testtest")
        self.assertIn("oz_test", response.data["thumbnail_img_url"])

    def test_create_exam_missing_field_fail(self) -> None:
        """필수 필드(title) 누락 시 실패 테스트"""
        data = {
            "subject_id": self.subject.pk,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_exam_list(self) -> None:
        """쪽지시험 목록 조회 테스트 (GET)"""
        for i in range(25):
            Exam.objects.create(title=f"시험 {i:02d}", subject=self.subject)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 25)
        self.assertEqual(len(response.data["exams"]), 10)

        response = self.client.get(self.url, {"page": 2, "size": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["page"], 2)
        self.assertEqual(len(response.data["exams"]), 5)

        response = self.client.get(self.url, {"search_keyword": "시험 0"})
        self.assertEqual(response.data["total_count"], 10)

        response = self.client.get(self.url, {"subject_id": 99})
        self.assertEqual(response.data["total_count"], 0)

        response = self.client.get(self.url, {"sort": "created_at", "order": "desc"})
        self.assertEqual(response.data["exams"][0]["title"], "시험 24")

    def test_get_exam_detail_success(self) -> None:
        """쪽지시험 상세 조회 성공 테스트"""
        exam = Exam.objects.create(title="시험 1", subject=self.subject)
        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], exam.pk)
        self.assertEqual(response.data["title"], "시험 1")

    def test_put_exam_detail_success(self) -> None:
        """쪽지시험 수정 성공 테스트 (제목 및 이미지 변경)"""
        exam = Exam.objects.create(title="test시험", subject=self.subject)

        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})
        img = "update_image/test_img_url"

        data = {"title": "updated title", "thumbnail_img": img}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "updated title")
        self.assertIn("update_image", response.data["thumbnail_img_url"])

    def test_delete_exam_success(self) -> None:
        """쪽지시험 삭제 성공 테스트"""
        exam = Exam.objects.create(title="delete_test시험", subject=self.subject)
        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], exam.pk)
        # 삭제 후 데이터베이스 확인
        self.assertFalse(Exam.objects.filter(pk=exam.pk).exists())

    def test_get_exam_detail_not_found(self) -> None:
        """존재하지 않는 ID 조회 시 404 확인 (커버리지 확보용)"""
        url = reverse("exam-detail", kwargs={"exam_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

