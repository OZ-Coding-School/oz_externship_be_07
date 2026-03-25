from typing import Any

from rest_framework import serializers


class AnalyticsItemSerializer(serializers.Serializer[Any]):
    period = serializers.CharField()
    count = serializers.IntegerField()


class AdminAnalyticsTrendSerializer(serializers.Serializer[Any]):
    interval = serializers.ChoiceField(choices=["monthly", "yearly"])
    from_date = serializers.DateField(format="%Y-%m-%d")
    to_date = serializers.DateField(format="%Y-%m-%d")
    total = serializers.IntegerField()
    items = AnalyticsItemSerializer(many=True)
