from typing import Any

from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]
from django.db.models import Count, Func
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.subject.models.enrollment_request_models import EnrollmentRequest


def get_student_enrollment_trend_service(interval: str) -> dict[str, Any]:
    now = timezone.now()
    now_floor = now.replace(hour=0, minute=0, second=0, microsecond=0)

    trunc_func: type[Func]

    if interval == "monthly":
        from_date = (now_floor - relativedelta(months=11)).replace(day=1)
        trunc_func = TruncMonth
        date_format = "%Y-%m"
        delta = relativedelta(months=1)

    elif interval == "yearly":
        from_date = (now_floor - relativedelta(years=4)).replace(month=1, day=1)
        trunc_func = TruncYear
        date_format = "%Y"
        delta = relativedelta(years=1)

    else:
        raise ValidationError("올바르지 않은 interval 형식입니다.")

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

        items.append(
            {
                "period": period_str,
                "count": count,
            }
        )
        total += count

        current += delta

    return {
        "interval": interval,
        "from_date": from_date.date(),
        "to_date": now.date(),
        "total": total,
        "items": items,
    }
