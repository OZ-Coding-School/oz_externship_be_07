from typing import Any

from rest_framework import serializers


class BaseReasonSerializer(serializers.Serializer[Any]):
    reason = serializers.CharField()
    reason_label = serializers.CharField()


class WithdrawalReasonCountItemSerializer(BaseReasonSerializer):
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class WithdrawalReasonCountSerializer(serializers.Serializer[Any]):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total = serializers.IntegerField()
    items = WithdrawalReasonCountItemSerializer(many=True)


class WithdrawalMonthlyReasonItemSerializer(serializers.Serializer[Any]):
    period = serializers.CharField()
    count = serializers.IntegerField()


class WithdrawalMonthlyReasonStatsSerializer(BaseReasonSerializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total = serializers.IntegerField()
    items = WithdrawalMonthlyReasonItemSerializer(many=True)
