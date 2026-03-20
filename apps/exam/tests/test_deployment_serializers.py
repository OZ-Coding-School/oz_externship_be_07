from __future__ import annotations

from django.test import SimpleTestCase
from rest_framework import serializers

from apps.exam.serializers.deployment_serializers import (
    DeploymentCheckCodeRequestSerializer,
    DeploymentListQuerySerializer,
    StringOrStringListField,
)


class StringOrStringListFieldTests(SimpleTestCase):
    def test_returns_string_when_value_is_string(self) -> None:
        field = StringOrStringListField()

        result = field.to_representation("abc")

        self.assertEqual(result, "abc")

    def test_returns_list_when_value_is_string_list(self) -> None:
        field = StringOrStringListField()

        result = field.to_representation(["a", "b"])

        self.assertEqual(result, ["a", "b"])

    def test_returns_none_when_value_is_none(self) -> None:
        field = StringOrStringListField()

        result = field.to_representation(None)

        self.assertIsNone(result)

    def test_raises_validation_error_when_value_is_invalid(self) -> None:
        field = StringOrStringListField()

        with self.assertRaises(serializers.ValidationError):
            field.to_representation([1, 2])


class DeploymentListQuerySerializerTests(SimpleTestCase):
    def test_validates_with_default_values(self) -> None:
        serializer = DeploymentListQuerySerializer(data={})

        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(serializer.validated_data["page"], 1)
        self.assertEqual(serializer.validated_data["status"], "all")

    def test_validates_with_explicit_values(self) -> None:
        serializer = DeploymentListQuerySerializer(
            data={
                "page": 2,
                "status": "pending",
            }
        )

        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(serializer.validated_data["page"], 2)
        self.assertEqual(serializer.validated_data["status"], "pending")

    def test_fails_when_page_is_less_than_one(self) -> None:
        serializer = DeploymentListQuerySerializer(data={"page": 0})

        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("page", serializer.errors)

    def test_fails_when_status_is_invalid(self) -> None:
        serializer = DeploymentListQuerySerializer(data={"status": "invalid"})

        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("status", serializer.errors)


class DeploymentCheckCodeRequestSerializerTests(SimpleTestCase):
    def test_validates_when_code_is_present(self) -> None:
        serializer = DeploymentCheckCodeRequestSerializer(data={"code": "124312"})

        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(serializer.validated_data["code"], "124312")

    def test_fails_when_code_is_missing(self) -> None:
        serializer = DeploymentCheckCodeRequestSerializer(data={})

        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("code", serializer.errors)
