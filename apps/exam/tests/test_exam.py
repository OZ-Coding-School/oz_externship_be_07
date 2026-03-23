import json
from typing import IO, Any, Dict, cast

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.subject.models.choices import SubjectStatus
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class ExamAPITest(APITestCase):
    # 속성 타입 선언 (attr-defined 에러 해결)
    admin_user: User
    target_user: User
    course: Course
    subject: Subject
    cls_exam: Exam
    question: ExamQuestion
    exam_data: Dict[str, Any]
    url: str

    @classmethod
    def setUpTestData(cls) -> None:  # 리턴 타입 명시
        """테스트 전체에서 사용할 기본 데이터 설정"""
        user_manager: Any = User.objects
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

        cls.target_user = user_manager.create(
            email="student@example.com",
            nickname="tstudent",
            name="홍길동",
            role="STUDENT",
            status="ACTIVATED",
            birthday="1998-08-29",
            phone_number="01012345678",
        )
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

        cls.cls_exam = Exam.objects.create(
            title="testclsexam",
            subject_id=cls.subject.pk,
            thumbnail_img_url="amazonaws.com/test_img_url",
        )

        cls.question = ExamQuestion.objects.create(
            exam=cls.cls_exam,
            question="testquestion",
            prompt="testprompt",
            blank_count=0,
            options_json=json.dumps(
                ["정적 타이핑 언어", "인터프리터 언어", "컴파일 방식만을 지원", "메모리 직접 관리 필요"]
            ),
            type="SINGLE_CHOICE",
            answer="testanswer",
            point=10,
            explanation="testexplanation",
        )

        cls.exam_data = {
            "title": "testexam",
            "subject_id": cls.subject.pk,
            "thumbnail_img": "amazonaws.com/test_img_url",
        }

        cls.url = reverse("exam-list-create")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_create_exam_success(self) -> None:
        """쪽지시험 생성 성공 테스트 (POST)"""

        data = self.exam_data.copy()
        data["title"] = "testtest"
        data["subject_id"] = self.subject.pk
        data["thumbnail_img"] = "oz_test/test_img_url"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 2)
        self.assertEqual(response.data["title"], "testtest")
        self.assertIn("oz_test", response.data["thumbnail_img_url"])

    def test_create_exam_missing_title_bad_request(self) -> None:
        """쪽지시험 생성 400 에러 : 필수 필드(title) 누락 시 실패 테스트"""
        data = {
            "subject_id": self.subject.pk,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "유효하지 않은 시험 생성 요청입니다.")

    def test_create_exam_unauthorized_denied(self) -> None:
        """쪽지시험 생성 401 에러코드 테스트"""
        data = self.exam_data.copy()
        data["title"] = "401test"
        self.client.force_authenticate(user=None)

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_create_exam_permission_denied(self) -> None:
        """쪽지시험 생성  403 에러 코드 테스트"""
        data = self.exam_data.copy()
        data["title"] = "403test"
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "쪽지시험 생성 권한이 없습니다.")

    def test_create_exam_subject_id_not_found(self) -> None:
        """쪽지시험 생성 404 에러 코드 테스트"""
        data = self.exam_data.copy()
        data["title"] = "404test"
        data["subject_id"] = 99
        data["thumbnail_img"] = "oz_test/test_img_url"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "해당 과목 정보를 찾을 수 없습니다.")

    def test_create_exam_same_title_conflict(self) -> None:
        """쪽지시험 생성 409 에러 코드 테스트"""
        existing_title = "Duplicate Title"
        data = self.exam_data.copy()
        data["title"] = existing_title

        self.client.post(self.url, data, format="json")

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error_detail"], "동일한 이름의 시험이 이미 존재합니다.")

    def test_get_exam_list(self) -> None:
        """쪽지시험 목록 조회 테스트 (GET)"""
        for i in range(25):
            Exam.objects.create(title=f"시험 {i:02d}", subject=self.subject)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 26)
        self.assertEqual(len(response.data["exams"]), 10)

        response = self.client.get(self.url, {"page": 2, "page_size": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["page"], 2)
        self.assertEqual(len(response.data["exams"]), 5)

        response = self.client.get(self.url, {"search_keyword": "시험 0"})
        self.assertEqual(response.data["total_count"], 10)

        response = self.client.get(self.url, {"subject_id": 99})
        self.assertEqual(response.data["total_count"], 0)

        response = self.client.get(self.url, {"sort": "created_at", "order": "desc"})
        self.assertEqual(response.data["exams"][0]["title"], "시험 24")

    def test_get_exam_unauthorized_denied(self) -> None:
        """쪽지시험 조회 401 에러코드 테스트"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_get_exam_permission_denied(self) -> None:
        """쪽지시험 조회 403 에러 코드 테스트"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "쪽지시험 목록 조회 권한이 없습니다.")

    def test_get_exam_detail_success(self) -> None:
        """쪽지시험 상세 조회 성공 테스트"""
        exam = Exam.objects.create(title="시험 1", subject_id=self.subject.pk)
        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], exam.pk)
        self.assertEqual(response.data["title"], "시험 1")

    def test_get_cls_exam_detail_success(self) -> None:
        """cls에 선언된 exam 상세조회 성공 테스트"""
        url = reverse("exam-detail", kwargs={"exam_id": self.cls_exam.pk})

        ExamQuestion.objects.create(
            exam=self.cls_exam,
            question="testquestion2",
            prompt="testprompt2",
            blank_count=0,
            options_json=json.dumps(["testoption1"]),
            type="SINGLE_CHOICE",
            answer="testanswer2",
            point=5,
            explanation="testexplanation2",
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.cls_exam.pk)
        self.assertEqual(response.data["title"], self.cls_exam.title)
        self.assertEqual(response.data["questions"][1]["question"], "testquestion2")

    def test_put_exam_detail_success(self) -> None:
        """쪽지시험 수정 성공 테스트 (제목 및 이미지 변경)"""
        exam = Exam.objects.create(title="test시험", subject_id=self.subject.pk)

        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})
        img = "update_image/test_img_url"

        data = {"title": "updated title", "thumbnail_img": img}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "updated title")
        self.assertIn("update_image", response.data["thumbnail_img_url"])

    def test_put_exam_unauthorized_denied(self) -> None:
        """쪽지시험 수정 401 에러코드 테스트"""
        exam = Exam.objects.create(title="test시험", subject_id=self.subject.pk)

        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})
        img = "update_image/test_img_url"

        data = {"title": "401test", "thumbnail_img": img}

        self.client.force_authenticate(user=None)

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_put_exam_permission_denied(self) -> None:
        """쪽지시험 수정  403 에러 코드 테스트"""
        exam = Exam.objects.create(title="test시험", subject_id=self.subject.pk)

        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})
        img = "update_image/test_img_url"

        data = {"title": "403test", "thumbnail_img": img}

        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "쪽지시험 수정 권한이 없습니다.")

    def test_put_exam_id_not_found(self) -> None:
        """쪽지시험 수정 404 에러 코드 테스트"""
        exam = Exam.objects.create(title="test시험", subject_id=self.subject.pk)

        url = reverse("exam-detail", kwargs={"exam_id": 99})
        img = "update_image/test_img_url"

        data = {"title": "404test", "thumbnail_img": img}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "수정할 쪽지시험 정보를 찾을 수 없습니다.")

    def test_put_exam_same_title_conflict(self) -> None:
        """쪽지시험 수정 409 에러 코드 테스트"""

        exam = Exam.objects.create(title="test시험", subject_id=self.subject.pk)

        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})
        img = "update_image/test_img_url"

        data = {"title": "testclsexam", "thumbnail_img": img}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error_detail"], "동일한 이름의 쪽지시험이 이미 존재합니다.")

    def test_delete_exam_success(self) -> None:
        """쪽지시험 삭제 성공 테스트"""
        exam = Exam.objects.create(title="delete_test시험", subject_id=self.subject.pk)
        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], exam.pk)
        # 삭제 후 데이터베이스 확인
        self.assertFalse(Exam.objects.filter(pk=exam.pk).exists())

    def test_delete_exam_detail_unauthorized_denied(self) -> None:
        """쪽지시험 삭제 401 에러 코드 테스트"""
        url = reverse("exam-detail", kwargs={"exam_id": self.cls_exam.pk})
        self.client.force_authenticate(user=None)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_delete_exam_detail_permission_denied(self) -> None:
        """쪽지시험 삭제 403 에러 코드 테스트"""
        url = reverse("exam-detail", kwargs={"exam_id": self.cls_exam.pk})

        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "쪽지시험 삭제 권한이 없습니다.")

    def test_delete_exam_detail_not_found(self) -> None:
        """존재하지 않는 ID 조회 시 404 확인"""
        url = reverse("exam-detail", kwargs={"exam_id": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "삭제하려는 쪽지시험 정보를 찾을 수 없습니다.")
