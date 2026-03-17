from django.core.exceptions import PermissionDenied
from django.test import TestCase

from apps.questions.models import QuestionCategories, Questions
from apps.questions.services.questions_update_services import QuestionUpdateService
from apps.users.models.models import User


class QuestionUpdateTest(TestCase):
    author: User
    other_user: User
    question: Questions

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create_user(
            email="test@test.com", name="오즈", nickname="깡통", phone_number="010-1234-1234", birthday="2000-04-01"
        )
        cls.other_user = User.objects.create_user(
            email="who@test.com", name="타인", nickname="화랑", phone_number="010-5467-1353", birthday="1997-02-14"
        )
        category = QuestionCategories.objects.create(name="Django")
        cls.question = Questions.objects.create(
            author=cls.author, category=category, title="Django의 기능", content="Django의 기능 설명와라라라"
        )

    # 수정 성공 테스트
    def test_update_question_success(self) -> None:
        updated_q: Questions = QuestionUpdateService.get_question_update(
            question_id=self.question.id,
            user=self.author,
            title="Django의 프레임워크",
            content="Restframework 소개글 쏼라쏼라",
        )
        self.assertEqual(updated_q.title, "Django의 프레임워크")
        self.assertEqual(updated_q.content, "Restframework 소개글 쏼라쏼라")

    # 수정 실패 테스트
    def test_update_question_permission_denied(self) -> None:
        with self.assertRaises(PermissionDenied):
            QuestionUpdateService.get_question_update(
                user=self.other_user,  # 작성자가 아닌 다른 유저
                question_id=self.question.id,
                title="수정 시도",
                content="내용 수정 시도",
            )
