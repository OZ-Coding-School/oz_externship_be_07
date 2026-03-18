from typing import Any, Dict

from rest_framework import serializers

from apps.subject.models.choices import CohortStatus
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course


class CohortCreateRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    number = serializers.IntegerField()
    max_student = serializers.IntegerField()

    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source="course",
        write_only=True,
    )

    start_date = serializers.DateField(
        required=True,
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
    )
    end_date = serializers.DateField(
        required=True,
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
    )
    status = serializers.ChoiceField(
        choices=CohortStatus.choices,
        required=False,
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({"end_date": ["종료일은 시작일 이후여야 합니다."]})

        return attrs


class CohortUpdateRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    number = serializers.IntegerField(required=False)
    max_student = serializers.IntegerField(required=False)
    start_date = serializers.DateField(
        required=False,
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
    )
    end_date = serializers.DateField(
        required=False,
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
    )
    status = serializers.ChoiceField(
        choices=CohortStatus.choices,
        required=False,
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        instance = self.instance if isinstance(self.instance, Cohort) else None

        start_date = attrs.get("start_date", getattr(instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(instance, "end_date", None))

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({"end_date": ["종료일은 시작일 이후여야 합니다."]})

        return attrs


class CohortCreateResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    detail = serializers.CharField()
    id = serializers.IntegerField()


class CohortListItemSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    number = serializers.IntegerField()
    status = serializers.CharField()


class CohortUpdateResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    number = serializers.IntegerField()
    max_student = serializers.IntegerField()
    start_date = serializers.DateField(format="%Y-%m-%d")
    end_date = serializers.DateField(format="%Y-%m-%d")
    status = serializers.CharField()
    updated_at = serializers.DateTimeField()


class CohortAvgScoreItemSerializer(serializers.Serializer[Dict[str, Any]]):
    name = serializers.CharField()
    score = serializers.IntegerField()


class CohortStudentItemSerializer(serializers.Serializer[Dict[str, Any]]):
    value = serializers.CharField()
    label = serializers.CharField()  # type: ignore[assignment]


class ErrorDetailStringSerializer(serializers.Serializer[Dict[str, Any]]):
    error_detail = serializers.CharField()
