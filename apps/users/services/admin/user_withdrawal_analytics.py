from datetime import datetime
from typing import Any

from django.db.models import Case, CharField, Count, F, Value, When
from django.db.models.functions import TruncMonth

from apps.users.choices import WithdrawalReason
from apps.users.models.models import Withdrawal


def get_withdrawal_reason_counts_service(from_date: datetime, to_date: datetime) -> dict[str, Any]:
    queryset = Withdrawal.objects.filter(created_at__range=(from_date, to_date))

    whens = [When(reason=code, then=Value(label)) for code, label in WithdrawalReason.choices]

    stats = (
        queryset.values("reason")
        .annotate(count=Count("id"), reason_label=Case(*whens, default=F("reason"), output_field=CharField()))
        .order_by("-count")
    )

    total_count = sum(s["count"] for s in stats)

    items = [
        {
            "reason": s["reason"],
            "reason_label": s["reason_label"],
            "count": s["count"],
            "percentage": round((s["count"] / total_count * 100), 2) if total_count > 0 else 0,
        }
        for s in stats
    ]

    return {"from_date": from_date.date(), "to_date": to_date.date(), "total": total_count, "items": items}


def get_monthly_withdrawal_reason_stats_service(reason: str, from_date: datetime, to_date: datetime) -> dict[str, Any]:
    queryset = Withdrawal.objects.filter(reason=reason, created_at__range=(from_date, to_date))

    stats = (
        queryset.annotate(period=TruncMonth("created_at"))
        .values("period")
        .annotate(count=Count("id"))
        .order_by("period")
    )

    reason_label = dict(WithdrawalReason.choices).get(reason, reason)

    items = []
    total_count = 0
    for s in stats:
        c = s["count"]
        items.append({"period": s["period"].strftime("%Y-%m"), "count": c})
        total_count += c

    return {
        "reason": reason,
        "reason_label": reason_label,
        "from_date": from_date.date(),
        "to_date": to_date.date(),
        "total": total_count,
        "items": items,
    }
