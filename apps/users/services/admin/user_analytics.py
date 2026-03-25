from datetime import datetime, timedelta
from typing import Any, Dict, Type

from django.db import models
from django.db.models import Count, Func
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone


def get_analytics_trend_service(
    model_class: Type[models.Model], interval: str, from_date_str: str | None = None, to_date_str: str | None = None
) -> Dict[str, Any]:
    now = timezone.now()

    from_date = datetime.strptime(from_date_str, "%Y-%m-%d") if from_date_str else (now - timedelta(days=365))
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d") if to_date_str else now

    trunc_func: Func
    if interval == "yearly":
        trunc_func = TruncYear("created_at")
        date_format = "%Y"
    else:
        trunc_func = TruncMonth("created_at")
        date_format = "%Y-%m"

    stats = (
        model_class._default_manager.filter(created_at__range=(from_date, to_date))
        .annotate(period=trunc_func)
        .values("period")
        .annotate(count=Count("id"))
        .order_by("period")
    )

    items = [{"period": s["period"].strftime(date_format), "count": s["count"]} for s in stats]

    return {
        "interval": interval,
        "from_date": from_date.date() if isinstance(from_date, datetime) else from_date,
        "to_date": to_date.date() if isinstance(to_date, datetime) else to_date,
        "total": sum(item["count"] for item in items),
        "items": items,
    }
