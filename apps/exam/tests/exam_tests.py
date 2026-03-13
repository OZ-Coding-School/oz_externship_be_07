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

    def test_create_exam_missing_field_fail(self):
        """필수 필드(title) 누락 시 실패 테스트"""
        data = {
            "subject_id": self.subject.id,
            # title 누락
        }
        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_exam_list(self):
        """쪽지시험 목록 조회 테스트 (GET)"""
        # 1. 테스트 데이터 25개 생성 (페이지네이션 확인용)
        for i in range(25):
            Exam.objects.create(title=f"시험 {i:02d}", subject=self.subject)

        # 2. 기본 조회 테스트 (1페이지, 기본 사이즈 10개 가정)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 25)  # 전체 개수
        self.assertEqual(len(response.data["exams"]), 10)  # 한 페이지당 개수

        # 3. 페이지네이션 파라미터 테스트 (2페이지, 사이즈 5개)
        response = self.client.get(self.url, {"page": 2, "size": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["page"], 2)
        self.assertEqual(len(response.data["exams"]), 5)

        # 4. 검색 키워드 테스트
        # "시험 0"으로 시작하는 데이터는 시험 00~09까지 10개여야 함
        response = self.client.get(self.url, {"search_keyword": "시험 0"})
        self.assertEqual(response.data["total_count"], 10)

        # 5. 과목 필터링 테스트
        # subject_id 를 99로 검색했을때 0개가 나와야 함
        response = self.client.get(self.url, {"subject_id": 99})
        self.assertEqual(response.data["total_count"], 0)

        # 6. 정렬 테스트 (최신순 - order=desc)
        response = self.client.get(self.url, {"sort": "created_at", "order": "desc"})
        self.assertEqual(response.data["exams"][0]["title"], "시험 24")

