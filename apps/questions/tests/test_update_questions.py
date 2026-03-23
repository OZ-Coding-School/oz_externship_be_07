from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import QuestionCategories, Questions
from apps.users.models.models import User


class QuestionUpdateTest(TestCase):
    author: User
    other_user: User
    question: Questions
    url: str
    client: APIClient

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
        cls.url = reverse("questions:question_detail_update", kwargs={"question_id": cls.question.id})

    def setUp(self) -> None:
        self.client = APIClient()

    # 인증되지 않은 유저
    def test_update_question_unauthorized(self) -> None:
        data = {"title": "수정시도"}
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 작성자가 아닌 유저
    def test_update_question_permission_denied(self) -> None:
        self.client.force_authenticate(user=self.other_user)
        data = {"title": "해킹시도", "content": "내용 변경"}
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "본인이 작성한 질문만 수정 가능합니다.")

    # 존재하지 않는 질문 ID
    def test_update_question_not_found(self) -> None:
        self.client.force_authenticate(user=self.author)
        invalid_url = reverse("questions:question_detail_update", kwargs={"question_id": 99999})
        data = {"title": "없는 제목"}
        response = self.client.put(invalid_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
