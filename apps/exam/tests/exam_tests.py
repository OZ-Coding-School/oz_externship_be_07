import tempfile

from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.exam.models.exam_models import Exam
from apps.subject.models.choices import SubjectStatus
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject


class ExamAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """테스트 전체에서 사용할 기본 데이터 설정 (과목 등)"""
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

    def _get_test_image(self):
        """테스트용 가짜 이미지 파일 생성"""
        file = tempfile.NamedTemporaryFile(suffix=".jpg")
        img = Image.new("RGB", (10, 10))
        img.save(file, format="JPEG")
        file.seek(0)
        return file

    def test_create_exam_success(self):
        """쪽지시험 생성 성공 테스트 (POST)"""
        img = self._get_test_image()

        data = self.exam_data.copy()
        data["title"] = "testtest"
        data["subject"] = self.subject.id
        data["thumbnail_img"] = img

        # parser_classes가 MultiPartParser이므로 format="multipart" 사용
        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 1)
        self.assertEqual(response.data["title"], "testtest")
        # 서비스 로직에 의해 생성된 S3 URL 경로 확인
        self.assertIn("amazonaws.com", response.data["thumbnail_img_url"])

    def test_get_exam_list(self):
        """쪽지시험 목록 조회 테스트 (GET)"""
        # 미리 데이터 생성
        Exam.objects.create(title="시험 1", subject=self.subject)
        Exam.objects.create(title="시험 2", subject=self.subject)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 뷰에서 정의한 공통 응답 구조(page, size, total_count, exams) 검증
        self.assertEqual(response.data["total_count"], 2)
        self.assertEqual(len(response.data["exams"]), 2)

    def test_create_exam_missing_field_fail(self):
        """필수 필드(title) 누락 시 실패 테스트"""
        data = {
            "subject_id": self.subject.id,
            # title 누락
        }
        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
