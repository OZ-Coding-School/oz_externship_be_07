import tempfile
from typing import IO, Any, Dict

from django.urls import reverse
from PIL import Image
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

    def _get_test_image(self) -> IO[Any]:  # 리턴 타입 명시 (파일 객체)
        """테스트용 가짜 이미지 파일 생성"""
        file = tempfile.NamedTemporaryFile(suffix=".jpg")
        img = Image.new("RGB", (10, 10))
        img.save(file, format="JPEG")
        file.seek(0)
        return file

    def test_create_exam_success(self) -> None:
        """쪽지시험 생성 성공 테스트 (POST)"""
        img = self._get_test_image()

        data = self.exam_data.copy()
        data["title"] = "testtest"
        data["subject"] = self.subject.pk
        data["thumbnail_img"] = img

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 1)
        self.assertEqual(response.data["title"], "testtest")
        self.assertIn("amazonaws.com", response.data["thumbnail_img_url"])

    def test_create_exam_missing_field_fail(self) -> None:
        """필수 필드(title) 누락 시 실패 테스트"""
        data = {
            "subject_id": self.subject.pk,
        }
        response = self.client.post(self.url, data, format="multipart")
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
