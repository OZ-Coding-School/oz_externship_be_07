import os
from typing import Optional

import google.generativeai as genai  # type: ignore[import-not-found]
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.users.models.models import User

from ..models import AnswerComments, AnswerImages, Answers, QuestionAiAnswers, Questions


class AnswerService:
    @staticmethod
    @transaction.atomic
    def create_answer(user: User, question_id: int, content: str, image_urls: Optional[list[str]] = None) -> Answers:
        question = get_object_or_404(Questions, id=question_id)
        answer = Answers.objects.create(author=user, questions=question, content=content)

        if image_urls:
            for url in image_urls:
                AnswerImages.objects.create(answer=answer, img_url=url)
        return answer

    @staticmethod
    @transaction.atomic
    def update_answer(user: User, answer_id: int, content: str, image_urls: Optional[list[str]] = None) -> Answers:
        answer = get_object_or_404(Answers, id=answer_id)

        # 본인 확인
        if answer.author != user:
            raise PermissionDenied("본인이 작성한 답변만 수정할 수 있습니다.")

        answer.content = content
        answer.save()

        # 이미지 수정 (삭제후재등록)
        if image_urls is not None:
            answer.images.all().delete()
            for url in image_urls:
                AnswerImages.objects.create(answer=answer, img_url=url)

        return answer

    @staticmethod
    def accept_answer(user: User, answer_id: int) -> Answers:
        answer = get_object_or_404(Answers, id=answer_id)

        # 질문자 본인 확인
        if answer.questions.author != user:
            raise PermissionDenied("본인이 작성한 질문의 답변만 채택할 수 있습니다.")

        # 중복 채택 방지
        if answer.questions.answers.filter(is_adopted=True).exists():
            raise ValidationError("이미 채택된 답변이 존재합니다.")

        answer.is_adopted = True
        answer.save()
        return answer

    @staticmethod
    def create_comment(user: User, answer_id: int, content: str) -> AnswerComments:
        # 글자수 제한
        if not content or len(content) > 500:
            raise ValidationError("댓글 내용은 1~500자 사이로 입력해야 합니다.")

        answer = get_object_or_404(Answers, id=answer_id)
        return AnswerComments.objects.create(author=user, answer=answer, content=content)

    @staticmethod
    def get_or_create_ai_answer(question_id: int) -> QuestionAiAnswers:
        # 명세서대로 404
        question = get_object_or_404(Questions, id=question_id)

        # 중복 생성 방지 (OneToOne)
        if hasattr(question, "ai_answers"):
            raise ValidationError("이미 AI가 답변을 생성했습니다.")

        # AI API 연동
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model_name = "gemini-2.5-pro"
        model = genai.GenerativeModel(model_name)

        prompt = f"질문 제목: {question.title}\n내용: {question.content}\n전문가로서 답변해줘."
        response = model.generate_content(prompt)

        # DB 저장
        ai_answer = QuestionAiAnswers.objects.create(questions=question, output=response.text, using_model=model_name)
        return ai_answer
