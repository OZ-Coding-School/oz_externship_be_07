import json
from typing import Any, Dict, cast

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.course_models import Course
from apps.subject.models.cohort_models import Cohort
from apps.users.models.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework.test import APIClient

class ExamAPITest(APITestCase):
    # 속성 타입 선언 (attr-defined 에러 해결)
    admin_user: User
    target_user: User
    course: Course
    cohort: Cohort
    exam: Exam
    exam_deployment: ExamDeployment
    exam_submission_data: dict[str, Any]

    create_url: str
    result_url: str

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

        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=40,
            start_date="2025-11-20T00:00:05.875842+09:00",
            end_date="2027-12-20T00:00:05.875842+09:00",
            status="IN_PROGRESS"
        )

        cls.exam = Exam.objects.create(
            title="testclsexam",
            subject_id=cls.subject.pk,
            thumbnail_img_url="amazonaws.com/test_img_url",
        )

        cls.exam_deployment = ExamDeployment.objects.create(
            cohort=cls.cohort,
            exam=cls.exam,
            duration_time="",
            access_code="testcode",
            open_at="2026-03-02 12:00:00",
            close_at="2026-03-30 12:00:00",
            questions_snapshot_json=json.dumps( [
                {
                  "question_id": 1,
                  "number": 1,
                  "type": "single_choice",
                  "question": "test_questions1",
                  "point": 10,
                  "prompt": null,
                  "blank_count": null,
                  "options": [
                    "상위 타입 값을 하위 타입 변수에 할당",
                    "하위 타입 값을 상위 타입 변수에 할당",
                    "서로소 유니온 타입 간 값은 일부 유니온 타입 변수에 할당",
                    "하위 타입 값을 상위 타입 변수에 할당"
                  ],
                  "answer_input": "하위 타입 값을 상위 타입 변수에 할당"
                },
                {
                  "question_id": 5,
                  "number": 5,
                  "type": "multiple_choice",
                  "question": "test_questions2",
                  "point": 10,
                  "prompt": null,
                  "blank_count": null,
                  "options": null,
                  "answer_input":["정적 타입 검사 지원", "자바스크립트와 호환됨"]
                }
              ]),
            status="ACTIVATED"
        )

        cls.exam_submission_data = {
            "exam_submission": cls.target_user,
            "deployment": cls.exam_deployment,
            "started_at": "2026-03-20T11:00:05.875842+09:00",
            "cheating_count": 1,
            "answers": json.dumps( [
                {
                  "question_id": 1,
                  "type": "single_choice",
                  "submitted_answer": "하위 타입 값을 상위 타입 변수에 할당"
                },
                {
                  "question_id": 2,
                  "type": "multiple_choice",
                  "submitted_answer": [
                    "정적 타입 검사 지원",
                    "자바스크립트와 호환됨",
                    "인터페이스와 제네릭을 지원함"
                  ]
                }
              ]),
            "score": 10,
            "correct_answer_count": 17
        }

        cls.create_url = reverse("exam-submission-create")
        cls.result_url = reverse("exam-submission-detail")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_create_exam_success(self) -> None:
        """쪽지시험 생성 성공 테스트 (POST)"""

        data = self.exam_submission_data.copy()
        data["title"] = "testtest"
        data["subject_id"] = self.subject.pk
        data["thumbnail_img"] = "oz_test/test_img_url"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 2)
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
        self.assertEqual(response.data["total_count"], 26)
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

    def test_delete_exam_success(self) -> None:
        """쪽지시험 삭제 성공 테스트"""
        exam = Exam.objects.create(title="delete_test시험", subject_id=self.subject.pk)
        url = reverse("exam-detail", kwargs={"exam_id": exam.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], exam.pk)
        # 삭제 후 데이터베이스 확인
        self.assertFalse(Exam.objects.filter(pk=exam.pk).exists())

    def test_get_exam_detail_not_found(self) -> None:
        """존재하지 않는 ID 조회 시 404 확인 (커버리지 확보용)"""
        url = reverse("exam-detail", kwargs={"exam_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access_fail(self) -> None:
        """인증되지 않은 사용자의 접근 실패 테스트"""
        self.client.force_authenticate(user=None)  # 인증 해제
        response = self.client.post(self.url, self.exam_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)