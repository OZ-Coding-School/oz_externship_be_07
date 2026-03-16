import json
from typing import List, Dict, Any, Optional, cast

from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion

class ExamQuestionService:
    @staticmethod
    def serialize(question: ExamQuestion) -> Dict[str, Any]:
        options: Any = None # 명시적 타입 지정
        if question.options_json:
            try:
                options = json.loads(question.options_json)
            except (ValueError, TypeError, json.JSONDecodeError):
                options = None

        return {
            "question_id": question.id,
            "type": question.type.lower(),
            "question": question.question,
            "prompt": question.prompt,
            "options": options,
            "blank_count": question.blank_count,
            "correct_answer": question.answer,
            "point": question.point,
            "explanation": question.explanation,
        }

    @staticmethod
    def list_by_exam(exam: Exam) -> List[Dict[str, Any]]:
        # objects 에러 발생 시 아래처럼 cast를 사용하거나 모델에 타입 힌트 추가 필요
        questions = ExamQuestion.objects.filter(exam=exam).order_by("id")
        return [ExamQuestionService.serialize(q) for q in questions]

    @staticmethod
    # 1. data: dict -> Dict[str, Any]로 수정
    def create_question(exam: Exam, data: Dict[str, Any]) -> ExamQuestion:
        options_json: Optional[str] = None
        if data.get("options") is not None:
            options_json = json.dumps(data["options"], ensure_ascii=False)

        # 2. Returning Any 에러 방지를 위한 cast 사용
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
        # 4. id, exam_id 인식 에러가 지속될 경우 로컬 변수 타입 명시
        exam_id: int = question.exam_id
        question_id: int = question.id
        question.delete()
        return {"exam_id": exam_id, "question_id": question_id}