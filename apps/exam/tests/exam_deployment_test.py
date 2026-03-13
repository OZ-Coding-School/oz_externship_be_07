import tempfile

from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.exam.models.exam_models import Exam
from apps.subject.models.choices import SubjectStatus
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject


class ExamDeploymentAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        테스트 전체에서 공통으로 사용할 기본 데이터 설정
        """
        cls.course = Course.objects.create(
            name="deployment-course",
            tag="deploy",
            description="deployment test course",
            thumbnail_img_url="amazonaws.com/test_course_img_url",
        )

        cls.subject = Subject.objects.create(
            course=cls.course,
            title="deployment-subject",
            number_of_days=5,
            number_of_hours=40,
            thumbnail_img_url="amazonaws.com/test_subject_img_url",
            status=SubjectStatus.ACTIVATED,
        )

        cls.url = reverse("exam-list-create")

    def _get_test_image(self):
        """
        테스트용 가짜 이미지 파일 생성
        """
        file = tempfile.NamedTemporaryFile(suffix=".jpg")
        img = Image.new("RGB", (10, 10))
        img.save(file, format="JPEG")
        file.seek(0)
        return file

    def test_get_exam_list_success(self):
        """
        쪽지시험 목록 조회 성공 테스트
        """
        Exam.objects.create(title="시험 1", subject=self.subject)
        Exam.objects.create(title="시험 2", subject=self.subject)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_count", response.data)
        self.assertIn("exams", response.data)
        self.assertEqual(response.data["total_count"], 2)
        self.assertEqual(len(response.data["exams"]), 2)

    def test_get_exam_list_empty_success(self):
        """
        데이터가 없어도 목록 조회는 정상 응답해야 함
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_count", response.data)
        self.assertIn("exams", response.data)
        self.assertEqual(response.data["total_count"], 0)
        self.assertEqual(len(response.data["exams"]), 0)

    def test_create_exam_success(self):
        """
        쪽지시험 생성 성공 테스트
        """
        img = self._get_test_image()

        data = {
            "title": "deployment-test-exam",
            "subject": self.subject.id,
            "thumbnail_img": img,
        }

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 1)
        self.assertEqual(response.data["title"], "deployment-test-exam")
        self.assertIn("thumbnail_img_url", response.data)
        self.assertIn("amazonaws.com", response.data["thumbnail_img_url"])

    def test_create_exam_missing_title_fail(self):
        """
        필수값 title 누락 시 생성 실패 테스트
        """
        img = self._get_test_image()

        data = {
            "subject": self.subject.id,
            "thumbnail_img": img,
        }

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exam_missing_subject_fail(self):
        """
        필수값 subject 누락 시 생성 실패 테스트
        """
        img = self._get_test_image()

        data = {
            "title": "subject-missing-exam",
            "thumbnail_img": img,
        }

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exam_invalid_subject_fail(self):
        """
        존재하지 않는 subject로 생성 요청 시 실패 테스트
        """
        img = self._get_test_image()

        data = {
            "title": "invalid-subject-exam",
            "subject": 999999,
            "thumbnail_img": img,
        }

        response = self.client.post(self.url, data, format="multipart")

        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )