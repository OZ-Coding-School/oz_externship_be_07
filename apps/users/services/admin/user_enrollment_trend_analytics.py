from datetime import timedelta
from typing import Any, Type

from django.db.models import Count, Func
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone

from apps.subject.models.enrollment_request_models import EnrollmentRequest


def get_student_enrollment_trend_service(interval: str) -> dict[str, Any]:
    now = timezone.now()
    trunc_func: Type[Func]

    if interval == "monthly":
        from_date = (now - timedelta(days=30 * 11)).replace(day=1)
        trunc_func = TruncMonth
        date_format = "%Y-%m"

    elif interval == "yearly":
        from_date = (now - timedelta(days=365 * 4)).replace(month=1, day=1)
        trunc_func = TruncYear
        date_format = "%Y"

    else:
        raise ValueError("Invalid interval")

    queryset = EnrollmentRequest.objects.filter(created_at__range=(from_date, now))

    stats = (
        queryset.annotate(period=trunc_func("created_at"))
        .values("period")
        .annotate(count=Count("id"))
        .order_by("period")
    )

    stats_dict = {s["period"].strftime(date_format): s["count"] for s in stats}

    items = []
    total = 0
    current = from_date

    while current <= now:
        period_str = current.strftime(date_format)
        count = stats_dict.get(period_str, 0)

        items.append({
            "period": period_str,
            "count": count,
        })

        total += count

        if interval == "monthly":
            current = current.replace(
                year=current.year + (current.month // 12),
                month=current.month % 12 + 1,
                day=1,
            )
        else:
            current = current.replace(year=current.year + 1, month=1, day=1)

    return {
        "interval": interval,
        "from_date": from_date.date(),
        "to_date": now.date(),
        "total": total,
        "items": items,
    }