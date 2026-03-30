from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import AnswerComments, Answers, QuestionCategories, Questions
from apps.users.models.models import User


class AdminQuestionDeleteTests(TestCase):
    admin_user: User
    normal_user: User
    category: QuestionCategories

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_superuser(
            email="admin@delete.com",
            password="admin123",
            name="관리자",
            nickname="관리자",
            phone_number="010-9999-0000",
            gender="MALE",
            birthday="1990-01-01",
        )
        cls.normal_user = User.objects.create_user(
            email="user@delete.com",
            password="user123",
            name="일반유저",
            nickname="일반유저",
            phone_number="010-8888-0000",
            gender="FEMALE",
            birthday="1995-01-01",
        )
        cls.category = QuestionCategories.objects.create(name="테스트")

    def _create_question_with_answers(self) -> tuple[Questions, list[Answers]]:
        question = Questions.objects.create(
            title="삭제 테스트 질문",
            content="삭제될 질문입니다.",
            author=self.admin_user,
            category=self.category,
        )
        answer1 = Answers.objects.create(questions=question, author=self.admin_user, content="답변1")
        answer2 = Answers.objects.create(questions=question, author=self.admin_user, content="답변2")
        AnswerComments.objects.create(answer=answer1, author=self.admin_user, content="댓글1")
        AnswerComments.objects.create(answer=answer1, author=self.admin_user, content="댓글2")
        AnswerComments.objects.create(answer=answer2, author=self.admin_user, content="댓글3")
        return question, [answer1, answer2]

    def test_delete_question_success(self) -> None:
        question, _ = self._create_question_with_answers()
        client = APIClient()
        client.force_authenticate(user=self.admin_user)

        url = reverse("admin_questions:admin-question-detail", kwargs={"question_id": question.id})
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question_id"], question.id)
        self.assertEqual(response.data["deleted_answer_count"], 2)
        self.assertEqual(response.data["deleted_comment_count"], 3)
        self.assertFalse(Questions.objects.filter(id=question.id).exists())

    def test_delete_question_not_found(self) -> None:
        client = APIClient()
        client.force_authenticate(user=self.admin_user)

        url = reverse("admin_questions:admin-question-detail", kwargs={"question_id": 99999})
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_question_no_permission(self) -> None:
        question, _ = self._create_question_with_answers()
        client = APIClient()
        client.force_authenticate(user=self.normal_user)

        url = reverse("admin_questions:admin-question-detail", kwargs={"question_id": question.id})
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAnswerDeleteTests(TestCase):
    admin_user: User
    normal_user: User
    category: QuestionCategories
    question: Questions

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_superuser(
            email="admin@ansdelete.com",
            password="admin123",
            name="관리자2",
            nickname="관리자2",
            phone_number="010-7777-0000",
            gender="MALE",
            birthday="1990-01-01",
        )
        cls.normal_user = User.objects.create_user(
            email="user@ansdelete.com",
            password="user123",
            name="일반유저2",
            nickname="일반유저2",
            phone_number="010-6666-0000",
            gender="FEMALE",
            birthday="1995-01-01",
        )
        cls.category = QuestionCategories.objects.create(name="테스트2")
        cls.question = Questions.objects.create(
            title="답변삭제 테스트",
            content="답변 삭제 테스트용 질문",
            author=cls.admin_user,
            category=cls.category,
        )

    def test_delete_answer_success(self) -> None:
        answer = Answers.objects.create(questions=self.question, author=self.admin_user, content="삭제할 답변")
        AnswerComments.objects.create(answer=answer, author=self.admin_user, content="댓글1")
        AnswerComments.objects.create(answer=answer, author=self.admin_user, content="댓글2")

        client = APIClient()
        client.force_authenticate(user=self.admin_user)

        url = reverse("admin_questions:admin-answer-delete", kwargs={"answer_id": answer.id})
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["answer_id"], answer.id)
        self.assertEqual(response.data["deleted_comment_count"], 2)
        self.assertFalse(Answers.objects.filter(id=answer.id).exists())

    def test_delete_answer_not_found(self) -> None:
        client = APIClient()
        client.force_authenticate(user=self.admin_user)

        url = reverse("admin_questions:admin-answer-delete", kwargs={"answer_id": 99999})
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_answer_no_permission(self) -> None:
        answer = Answers.objects.create(questions=self.question, author=self.admin_user, content="권한 테스트")

        client = APIClient()
        client.force_authenticate(user=self.normal_user)

        url = reverse("admin_questions:admin-answer-delete", kwargs={"answer_id": answer.id})
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
