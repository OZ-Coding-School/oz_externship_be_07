from rest_framework import serializers

from apps.subject.models.cohort_models import Cohort

COHORT_STATUS_CHOICES = ("PREPARING", "IN_PROGRESS", "FINISHED")


class CohortCreateRequestSerializer(serializers.Serializer):
    course = serializers.IntegerField(required=True)
    number = serializers.IntegerField(required=True)
    max_student = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True, format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    end_date = serializers.DateField(required=True, format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    status = serializers.ChoiceField(choices=COHORT_STATUS_CHOICES, required=False)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({"end_date": ["종료일은 시작일 이후여야 합니다."]})

        return attrs


class CohortUpdateRequestSerializer(serializers.Serializer):
    number = serializers.IntegerField(required=False)
    max_student = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False, format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    end_date = serializers.DateField(required=False, format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    status = serializers.ChoiceField(choices=COHORT_STATUS_CHOICES, required=False)

    def validate(self, attrs):
        instance: Cohort = getattr(self, "instance", None)
        start_date = attrs.get("start_date", instance.start_date if instance else None)
        end_date = attrs.get("end_date", instance.end_date if instance else None)

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({"end_date": ["종료일은 시작일 이후여야 합니다."]})

        return attrs


class CohortCreateResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    id = serializers.IntegerField()


class CohortListItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course = serializers.IntegerField()
    number = serializers.IntegerField()
    status = serializers.CharField()


class CohortUpdateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course = serializers.IntegerField()
    number = serializers.IntegerField()
    max_student = serializers.IntegerField()
    start_date = serializers.DateField(format="%Y-%m-%d")
    end_date = serializers.DateField(format="%Y-%m-%d")
    status = serializers.CharField()
    updated_at = serializers.DateTimeField()


class CohortStudentItemSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class ErrorDetailStringSerializer(serializers.Serializer):
    error_detail = serializers.CharField()


class ErrorDetailFieldSerializer(serializers.Serializer):
    error_detail = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
