import json
from typing import Any, Dict, Optional

from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion


class ExamQuestionConflictError(Exception):
    pass


class ExamQuestionService:

    @staticmethod
    # 1. data: dict -> Dict[str, Any]로 수정
    def create_question(exam: Exam, data: Dict[str, Any]) -> ExamQuestion:
        options_json: Optional[str] = None
        if data.get("options") is not None:
            options_json = json.dumps(data["options"], ensure_ascii=False)

        return ExamQuestion.objects.create(
            exam=exam,
            type=data["type"],
            question=data["question"],
            prompt=data.get("prompt"),
            options_json=options_json,
            blank_count=data.get("blank_count"),
            answer=data["correct_answer"],
            point=data["point"],
            explanation=data["explanation"],
        )

    @staticmethod
    # 3. data: dict -> Dict[str, Any]로 수정
    def update_question(question: ExamQuestion, data: Dict[str, Any]) -> ExamQuestion:
        if "options" in data:
            question.options_json = (
                json.dumps(data["options"], ensure_ascii=False) if data["options"] is not None else None
            )
        if "type" in data:
            question.type = data["type"]
        if "question" in data:
            question.question = data["question"]
        if "prompt" in data:
            question.prompt = data["prompt"]
        if "blank_count" in data:
            question.blank_count = data["blank_count"]
        if "correct_answer" in data:
            question.answer = data["correct_answer"]
        if "point" in data:
            question.point = data["point"]
        if "explanation" in data:
            question.explanation = data["explanation"]

        question.save()
        return question

    @staticmethod
    def delete_question(question: ExamQuestion) -> Dict[str, Any]:

        exam_id: int = question.exam_id
        question_id: int = question.id
        question.delete()
        return {"exam_id": exam_id, "question_id": question_id}
