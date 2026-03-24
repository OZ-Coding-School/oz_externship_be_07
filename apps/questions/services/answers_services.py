import os

from django.db import transaction
from django.shortcuts import get_object_or_404
from google import genai
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.users.models.models import User

from ..models import AnswerComments, AnswerImages, Answers, QuestionAiAnswers, Questions


class AnswerService:

    # 답변 등록
    @staticmethod
    @transaction.atomic
    def create_answer(user: User, question_id: int, content: str, image_urls: list[str] | None = None) -> Answers:
        question = get_object_or_404(Questions, id=question_id)
        answer = Answers.objects.create(author=user, questions=question, content=content)

        if image_urls:
            AnswerImages.objects.bulk_create([AnswerImages(answer=answer, img_url=url) for url in image_urls])
        return answer

    # 답변 수정
    @staticmethod
    @transaction.atomic
    def update_answer(user: User, answer_id: int, content: str, image_urls: list[str] | None = None) -> Answers:
        answer = get_object_or_404(Answers, id=answer_id)

        if answer.author != user:
            raise PermissionDenied("본인이 작성한 답변만 수정할 수 있습니다.")

        answer.content = content
        answer.save()

        if image_urls is not None:
            answer.images.all().delete()
            AnswerImages.objects.bulk_create([AnswerImages(answer=answer, img_url=url) for url in image_urls])
        return answer

    # 답변 채택
    @staticmethod
    def accept_answer(user: User, answer_id: int) -> Answers:
        answer = get_object_or_404(Answers, id=answer_id)

        if answer.questions.author != user:
            raise PermissionDenied("본인이 작성한 질문의 답변만 채택할 수 있습니다.")

        if answer.questions.answers.filter(is_adopted=True).exists():
            raise ValidationError("이미 채택된 답변이 존재합니다.")

        answer.is_adopted = True
        answer.save()
        return answer

    # 답변 댓글 등록
    @staticmethod
    def create_comment(user: User, answer_id: int, content: str) -> AnswerComments:
        answer = get_object_or_404(Answers, id=answer_id)
        return AnswerComments.objects.create(author=user, answer=answer, content=content)

    # AI 답변 생성/조회
    @staticmethod
    def get_or_create_ai_answer(question_id: int) -> QuestionAiAnswers:
        question = get_object_or_404(Questions, id=question_id)

        if hasattr(question, "ai_answers"):
            raise ValidationError("이미 AI가 답변을 생성했습니다.")

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        model_name = "gemini-2.5-flash"
        prompt = f"질문 제목: {question.title}\n내용: {question.content}\n전문가로서 답변해줘."

        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            
            return QuestionAiAnswers.objects.create(
            questions=question,
            output=response.text or "",
            using_model=model_name,
            )
        except Exception as e:
            logger.error(f"[AI 답변 생성 실패] Question ID{question_id}: {str(e)}")
            return None