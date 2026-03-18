from django.test import SimpleTestCase

from apps.exam.serializers.exam_question_serializers import (
    ExamQuestionCreateSerializer,
    ExamQuestionDeleteResponseSerializer,
    ExamQuestionResponseSerializer,
    ExamQuestionUpdateSerializer,
)


class ExamQuestionSerializerTest(SimpleTestCase):
    def test_create_serializer_accepts_valid_payload(self) -> None:
        payload = {
            "type": "SINGLE_CHOICE",
            "question": "테스트 문제",
            "prompt": "보기를 읽고 정답을 고르세요.",
            "options": ["1번", "2번", "3번"],
            "blank_count": None,
            "correct_answer": {"value": "2번"},
            "point": 10,
            "explanation": "정답은 2번입니다.",
        }

        serializer = ExamQuestionCreateSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertEqual(serializer.validated_data["type"], "SINGLE_CHOICE")
        self.assertEqual(serializer.validated_data["point"], 10)

    def test_create_serializer_allows_optional_fields_to_be_omitted(self) -> None:
        payload = {
            "type": "SHORT_ANSWER",
            "question": "약자를 쓰세요.",
            "correct_answer": {"value": "Django"},
            "point": 5,
            "explanation": "장고가 정답입니다.",
        }

        serializer = ExamQuestionCreateSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertNotIn("prompt", serializer.validated_data)
        self.assertNotIn("options", serializer.validated_data)
        self.assertNotIn("blank_count", serializer.validated_data)

    def test_create_serializer_rejects_invalid_type(self) -> None:
        payload = {
            "type": "single_choice",
            "question": "테스트 문제",
            "correct_answer": {"value": "A"},
            "point": 10,
            "explanation": "해설",
        }

        serializer = ExamQuestionCreateSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("type", serializer.errors)

    def test_create_serializer_rejects_point_out_of_range(self) -> None:
        payload = {
            "type": "OX",
            "question": "장고는 파이썬 프레임워크다.",
            "correct_answer": {"value": "O"},
            "point": 101,
            "explanation": "맞는 설명입니다.",
        }

        serializer = ExamQuestionCreateSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("point", serializer.errors)

    def test_update_serializer_uses_same_validation_as_create_serializer(self) -> None:
        payload = {
            "type": "FULL_BLANK",
            "question": "빈칸을 채우세요.",
            "prompt": None,
            "options": None,
            "blank_count": 2,
            "correct_answer": {"values": ["A", "B"]},
            "point": 20,
            "explanation": "순서대로 입력하면 됩니다.",
        }

        serializer = ExamQuestionUpdateSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertEqual(serializer.validated_data["blank_count"], 2)

    def test_response_serializer_serializes_nullable_fields(self) -> None:
        serializer = ExamQuestionResponseSerializer(
            data={
                "question_id": 1,
                "type": "SHORT_ANSWER",
                "question": "정답을 입력하세요.",
                "prompt": None,
                "options": None,
                "blank_count": None,
                "correct_answer": {"value": "정답"},
                "point": 3,
                "explanation": "예시 해설입니다.",
            }
        )

        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertIsNone(serializer.validated_data["prompt"])
        self.assertIsNone(serializer.validated_data["options"])
        self.assertIsNone(serializer.validated_data["blank_count"])

    def test_delete_response_serializer_requires_exam_id_and_question_id(self) -> None:
        serializer = ExamQuestionDeleteResponseSerializer(
            data={
                "exam_id": 7,
                "question_id": 11,
            }
        )

        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertEqual(serializer.validated_data["exam_id"], 7)
        self.assertEqual(serializer.validated_data["question_id"], 11)
