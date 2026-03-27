import json
from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.choices import SubjectStatus
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class ExamSubmissionAPITest(APITestCase):
    admin_user: User
    student_user: User
    other_student_user: User
    course: Course
    subject: Subject
    exam: Exam
    deployment: ExamDeployment
    question: ExamQuestion
    cohort: Cohort
    submission: ExamSubmission
    submission_data: dict[str, Any]
    list_url: str

    @classmethod
    def setUpTestData(cls) -> None:
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

        cls.student_user = user_manager.create(
            email="student@example.com",
            nickname="tstudent",
            name="홍길동",
            role="STUDENT",
            status="ACTIVATED",
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        cls.other_student_user = user_manager.create(
            email="other@example.com",
            nickname="tother",
            name="김철수",
            role="STUDENT",
            status="ACTIVATED",
            birthday="1999-03-15",
            phone_number="01087654321",
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
        cls.exam = Exam.objects.create(
            title="testexam",
            subject_id=cls.subject.pk,
            thumbnail_img_url="amazonaws.com/test_img_url",
        )
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date="2025-01-01",
            end_date="2025-12-31",
        )

        # 1. 실제 ExamQuestion 모델 생성 (스냅샷과 ID를 맞추기 위해 순차 생성)
        questions_data = [
            {
                "id": 6,
                "question": "React에서 상태 관리를 위한 Hook은?",
                "type": "SINGLE_CHOICE",
                "options": ["useEffect", "useState", "useRef", "useMemo"],
                "answer": ["useState"],
                "point": 10,
                "explanation": "useState는 컴포넌트의 상태를 관리합니다.",
            },
            {
                "id": 7,
                "question": "React 컴포넌트는 반드시 클래스로 작성해야 한다.",
                "type": "OX",
                "options": ["O", "X"],
                "answer": ["X"],
                "point": 5,
                "explanation": "함수형 컴포넌트도 사용 가능합니다.",
            },
            {
                "id": 8,
                "question": "JSX에서 JavaScript 표현식을 삽입할 때 사용하는 기호는?",
                "type": "SHORT_ANSWER",
                "options": None,
                "answer": ["{}"],
                "point": 10,
                "explanation": "중괄호 {}로 JS 표현식을 삽입합니다.",
            },
            {
                "id": 13,
                "question": "다음 중 React의 Hook을 모두 고르시오.",
                "type": "MULTIPLE_CHOICE",
                "options": ["useState", "useEffect", "getElementById", "useRef"],
                "answer": ["useState", "useEffect", "useRef"],
                "point": 10,
                "explanation": "getElementById는 DOM API이며 React Hook이 아닙니다.",
            },
            {
                "id": 14,
                "question": "React 컴포넌트 렌더링 순서를 정렬하세요.",
                "type": "ORDERING",
                "options": ["state 변경", "render 호출", "가상 DOM 비교", "실제 DOM 업데이트"],
                "answer": ["state 변경", "render 호출", "가상 DOM 비교", "실제 DOM 업데이트"],
                "point": 10,
                "explanation": "state 변경 → render → 가상 DOM diffing → 실제 DOM 반영 순서입니다.",
            },
            {
                "id": 15,
                "question": "React에서 컴포넌트 간 데이터를 전달할 때 ___를 사용한다.",
                "type": "FILL_BLANK",
                "options": None,
                "answer": ["props"],
                "point": 10,
                "explanation": "props는 부모에서 자식 컴포넌트로 데이터를 전달하는 방법입니다.",
                "blank_count": 1,
                "prompt": "React에서 컴포넌트 간 데이터를 전달할 때 ___를 사용한다.",
            },
        ]

        snapshot_list = []
        for q in questions_data:
            question_obj = ExamQuestion.objects.create(  # type: ignore
                id=q["id"],
                exam=cls.exam,
                question=q["question"],
                type=q["type"],
                options_json=json.dumps(q["options"]) if q["options"] else None,
                answer=q["answer"],
                point=q["point"],
                explanation=q["explanation"],
                blank_count=q.get("blank_count", 0),
                prompt=q.get("prompt"),
            )
            # 2. Deployment에 들어갈 스냅샷 리스트 빌드
            snapshot_list.append(
                {
                    "id": question_obj.id,
                    "question": question_obj.question,
                    "type": question_obj.type,
                    "options_json": question_obj.options_json,
                    "answer": question_obj.answer,
                    "point": question_obj.point,
                    "explanation": question_obj.explanation,
                    "blank_count": question_obj.blank_count,
                    "prompt": question_obj.prompt,
                }
            )

        cls.deployment = ExamDeployment.objects.create(
            cohort=cls.cohort,
            exam=cls.exam,
            duration_time=60,
            access_code="react123",
            open_at="2025-01-01T00:00:00Z",
            close_at="2026-12-31T23:59:59Z",
            questions_snapshot_json=snapshot_list,
        )

        # 3. 요청 데이터 설정 (request.json 내용 반영)
        cls.submission_data = {
            "deployment_id": cls.deployment.pk,
            "started_at": "2026-03-27T13:18:06.417Z",
            "cheating_count": 0,
            "answers": [
                {"question_id": 6, "type": "SINGLE_CHOICE", "submitted_answer": "useState"},
                {"question_id": 7, "type": "OX", "submitted_answer": "X"},
                {"question_id": 8, "type": "SHORT_ANSWER", "submitted_answer": "{}"},
                {"question_id": 13, "type": "MULTIPLE_CHOICE", "submitted_answer": ["useState", "useEffect", "useRef"]},
                {
                    "question_id": 14,
                    "type": "ORDERING",
                    "submitted_answer": ["state 변경", "render 호출", "가상 DOM 비교", "실제 DOM 업데이트"],
                },
                {"question_id": 15, "type": "FILL_BLANK", "submitted_answer": ["props"]},
            ],
        }
        cls.list_url = reverse("exam-submission-create")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student_user))

    def test_create_and_get_detail_integration(self) -> None:
        """제출 생성 후 상세 조회 시 데이터 일관성 검증 통합 테스트"""

        # [Step 1] 제출 API 호출
        create_response = self.client.post(self.list_url, self.submission_data, format="json")
        # print("\n" + "=" * 20 + " [POST] SUBMISSION CREATE RESPONSE " + "=" * 20)
        # print(json.dumps(create_response.data, indent=2, ensure_ascii=False))

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        submission_id = create_response.data["submission_id"]
        # 모든 정답을 맞췄으므로 총점 55점 (10+5+10+10+10+10) 검증
        self.assertEqual(create_response.data["score"], 55)
        self.assertEqual(create_response.data["correct_answer_count"], 6)

        # [Step 2] 상세 조회 API 호출
        detail_url = reverse("exam-submission-detail", kwargs={"submission_id": submission_id})
        detail_response = self.client.get(detail_url)

        # print("\n" + "=" * 20 + " [GET] SUBMISSION DETAIL RESPONSE " + "=" * 20)
        # print(json.dumps(detail_response.data, indent=2, ensure_ascii=False))

        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        res_data = detail_response.data

        # 기본 정보 검증
        self.assertEqual(res_data["id"], submission_id)
        self.assertEqual(res_data["total_score"], 55)

        # questions 상세 검증 (제출 답변과 ID가 null이 아닌지 확인)
        questions = res_data["questions"]
        self.assertEqual(len(questions), 6)

        for q in questions:
            self.assertIsNotNone(q["id"])
            self.assertIsNotNone(q["submitted_answer"])
            self.assertTrue(q["is_correct"], f"Question ID {q['id']} should be correct")

        # 특정 문제(다중 선택)의 데이터 구조 확인
        multiple_choice_q = next(q for q in questions if q["id"] == 13)
        self.assertEqual(multiple_choice_q["submitted_answer"], ["useState", "useEffect", "useRef"])
        self.assertEqual(multiple_choice_q["type"], "MULTIPLE_CHOICE")

    def test_create_submission_with_string_snapshot(self) -> None:
        """
        questions_snapshot_json이 리스트가 아닌 JSON 문자열(str)일 때
        내부적으로 json.loads()가 정상 작동하는지 테스트
        """
        # 1. snapshot을 문자열로 직렬화하여 새로운 Deployment 생성
        string_snapshot = json.dumps(
            [
                {
                    "id": 99,
                    "question": "JSON 문자열 스냅샷 테스트",
                    "type": "SINGLE_CHOICE",
                    "options": ["A", "B"],
                    "answer": ["A"],
                    "point": 10,
                }
            ]
        )

        str_deployment = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam,
            duration_time=30,
            access_code="string_test",
            open_at="2025-01-01T00:00:00Z",
            close_at="2026-12-31T23:59:59Z",
            questions_snapshot_json=string_snapshot,  # 여기서 문자열 주입
        )

        # 2. 해당 Deployment로 제출 데이터 구성
        submission_data = {
            "deployment_id": str_deployment.pk,
            "started_at": "2026-03-27T14:00:00Z",
            "answers": [{"question_id": 99, "type": "SINGLE_CHOICE", "submitted_answer": "A"}],
        }

        # 3. API 호출 (서비스 레이어의 _calculate_score 내부에서 isinstance(snapshot, str) 로직이 실행됨)
        response = self.client.post(self.list_url, submission_data, format="json")

        # 4. 검증: 문자열이었던 snapshot이 정상 파싱되어 점수가 계산되었는지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 10)
        self.assertEqual(response.data["correct_answer_count"], 1)

        # 5. 상세 조회(Serializer의 _build_questions 로직) 검증
        detail_url = reverse("exam-submission-detail", kwargs={"submission_id": response.data["submission_id"]})
        detail_response = self.client.get(detail_url)

        # Serializer 내의 _build_questions에서도 isinstance(snapshot, str) 로직이 성공해야 함
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["questions"][0]["id"], 99)
        self.assertEqual(detail_response.data["questions"][0]["question"], "JSON 문자열 스냅샷 테스트")
