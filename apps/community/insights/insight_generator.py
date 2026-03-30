from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Any, Callable, Literal, TypedDict

from apps.community.core.constants import (
    INSIGHT_ACTIVATION_RATE_GOOD,
    INSIGHT_AVG_COMMENTS_GOOD,
    INSIGHT_AVG_COMMENTS_LOW,
    INSIGHT_AVG_LIKES_LOW,
    INSIGHT_CATEGORY_SKEW_MIN_POSTS,
    INSIGHT_RESPONSE_RATE_CRITICAL,
    INSIGHT_RESPONSE_RATE_GOOD,
    INSIGHT_RESPONSE_RATE_WARNING,
    INSIGHT_SETTLEMENT_RATE_GOOD,
    INSIGHT_SETTLEMENT_RATE_WARNING,
    INSIGHT_SETTLEMENT_MIN_USERS,
    INSIGHT_TARGET_ACTIVATION_RATE,
    INSIGHT_TARGET_AVG_COMMENTS,
    INSIGHT_TARGET_RESPONSE_RATE,
    INSIGHT_TARGET_SETTLEMENT_RATE,
    INSIGHT_TOP1_CATEGORY_SHARE_CRITICAL,
    INSIGHT_TOP1_CATEGORY_SHARE_WARNING,
    INSIGHT_WEAKEST_TIEBREAK_ORDER,
)

InsightLevel = Literal["CRITICAL", "WARNING", "GOOD", "INFO"]


@dataclass(frozen=True)
class InsightRule:
    rule_id: str
    group: str
    priority: int
    level: InsightLevel
    title: str
    condition: Callable[[dict[str, Any]], bool]
    message: Callable[[dict[str, Any]], str]


class Finding(TypedDict):
    rule_id: str
    group: str
    priority: int
    level: InsightLevel
    title: str
    message: str


def _to_float(value: Any) -> float:
    return float(value) if value is not None else 0.0


def _percent_text(value: float) -> str:
    return f"{value:.1f}%"


def _num_text(value: float) -> str:
    return f"{value:.2f}"


def _safe_ratio(current: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return current / target

def _category_post_total(m: dict[str, Any]) -> int:
    counts = m.get("active_category_post_counts", {})
    if not isinstance(counts, dict):
        return 0
    return sum(int(v) for v in counts.values())


def _build_rules() -> list[InsightRule]:
    return [
        InsightRule(
            rule_id="response_critical",
            group="response_rate",
            priority=10,
            level="CRITICAL",
            title="응답 지연",
            condition=lambda m: _to_float(m["response_rate_within_24h"]) < INSIGHT_RESPONSE_RATE_CRITICAL,
            message=lambda m: (
                f"24시간 내 응답률이 {_percent_text(_to_float(m['response_rate_within_24h']))}로 매우 낮습니다. "
                "글이 무응답 상태로 방치되면 이탈로 이어집니다. 무응답 상태인 질문형 글에 즉시 답변해 주세요. "
            ),
        ),
        InsightRule(
            rule_id="response_warning",
            group="response_rate",
            priority=20,
            level="WARNING",
            title="응답 지연",
            condition=lambda m: _to_float(m["response_rate_within_24h"]) < INSIGHT_RESPONSE_RATE_WARNING,
            message=lambda m: (
                f"24시간 내 응답률이 {_percent_text(_to_float(m['response_rate_within_24h']))}로 낮습니다. "
                "무응답 글을 확인하고 활발한 멤버를 멘션하거나, 해당 글을 상위로 끌어올려 답변을 유도해 주세요. "
            ),
        ),
        InsightRule(
            rule_id="settlement_warning",
            group="settlement_rate",
            priority=30,
            level="WARNING",
            title="신규 이탈",
            condition=lambda m: int(m["new_users_count"]) >= INSIGHT_SETTLEMENT_MIN_USERS
            and _to_float(m["new_user_settlement_rate"]) < INSIGHT_SETTLEMENT_RATE_WARNING,
            message=lambda m: (
                f"신규 정착률이 {_percent_text(_to_float(m['new_user_settlement_rate']))}로 낮습니다. "
                "신규 유저 대상 온보딩 안내를 제공하고, 시작용 공지/질문 글로 첫 활동을 유도해 주세요."
                "또는 신규 유저 대상 간단한 참여 유도 콘텐츠를 추가해 보세요. "
            ),
        ),
        InsightRule(
            rule_id="conversation_low_both",
            group="conversation",
            priority=40,
            level="WARNING",
            title="대화 저조",
            condition=lambda m: _to_float(m["avg_comments_per_post"]) < INSIGHT_AVG_COMMENTS_LOW
            and _to_float(m["avg_likes_per_post"]) < INSIGHT_AVG_LIKES_LOW,
            message=lambda m: (
                f"게시글당 댓글 {_num_text(_to_float(m['avg_comments_per_post']))}개, "
                f"좋아요 {_num_text(_to_float(m['avg_likes_per_post']))}개로 전반적인 반응이 낮습니다. "
                "질문형/참여형 글을 작성하거나, 관심을 끌 주제를 던져 참여를 유도해주세요. "
            ),
        ),
        InsightRule(
            rule_id="conversation_low_comments",
            group="conversation",
            priority=50,
            level="WARNING",
            title="대화 저조",
            condition=lambda m: _to_float(m["avg_comments_per_post"]) < INSIGHT_AVG_COMMENTS_LOW
            and _to_float(m["avg_likes_per_post"]) >= INSIGHT_AVG_LIKES_LOW,
            message=lambda m: (
                f"게시글당 댓글이 {_num_text(_to_float(m['avg_comments_per_post']))}개로 관심에 비해 대화가 이어지지 않습니다. "
                "반응이 있는 글에 질문형 댓글로 대화를 유도해 주세요. "
            ),
        ),
        InsightRule(
            rule_id="category_skew_critical",
            group="category_skew",
            priority=60,
            level="CRITICAL",
            title="카테고리 편중",
            condition=lambda m: _category_post_total(m) >= INSIGHT_CATEGORY_SKEW_MIN_POSTS
            and _to_float(m["top1_category_share"]) > INSIGHT_TOP1_CATEGORY_SHARE_CRITICAL,
            message=lambda m: (
                f"최다 카테고리 비중이 {_percent_text(_to_float(m['top1_category_share']))}로 심각하게 편중되어 있습니다. "
                "특정 주제에 콘텐츠가 집중되면 다양한 유저 참여가 제한됩니다. "
                "다른 카테고리에 관리자 주도 콘텐츠를 등록해 주제 다양성을 회복해 주세요. "
            ),
        ),
        InsightRule(
            rule_id="category_skew_warning",
            group="category_skew",
            priority=70,
            level="WARNING",
            title="카테고리 편중",
            condition=lambda m: _category_post_total(m) >= INSIGHT_CATEGORY_SKEW_MIN_POSTS
            and _to_float(m["top1_category_share"]) > INSIGHT_TOP1_CATEGORY_SHARE_WARNING,
            message=lambda m: (
                f"최다 카테고리 비중이 {_percent_text(_to_float(m['top1_category_share']))}입니다. "
                "균형 잡힌 주제 운영이 필요해 보입니다. "
                "관심범위가 좁아지지 않도록 참여비중이 낮은 카테고리 위주로 콘텐츠를 보강해 주세요. "
            ),
        ),
    ]


def _is_good(metrics: dict[str, Any], critical_count: int, warning_count: int) -> bool:
    # GOOD 게이트: CRITICAL/WARNING 없어야 하며 핵심 4조건 중 3개 이상 충족
    if critical_count > 0 or warning_count > 0:
        return False

    core_hits = 0
    if _to_float(metrics["response_rate_within_24h"]) >= INSIGHT_RESPONSE_RATE_GOOD:
        core_hits += 1
    if _to_float(metrics["avg_comments_per_post"]) >= INSIGHT_AVG_COMMENTS_GOOD:
        core_hits += 1
    if _to_float(metrics["user_activation_rate"]) >= INSIGHT_ACTIVATION_RATE_GOOD:
        core_hits += 1
    if (
        int(metrics["new_users_count"]) == 0
        or _to_float(metrics["new_user_settlement_rate"]) >= INSIGHT_SETTLEMENT_RATE_GOOD
    ):
        core_hits += 1

    return core_hits >= 3


WEAKEST_MESSAGE_BUILDERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "user_activation_rate": lambda m: (
        f"활성화율이 {_percent_text(_to_float(m['user_activation_rate']))}입니다. "
        "참여를 더 끌어올릴 여지가 있습니다. "
        "흥미로운 주제를 담은 공지를 올리거나 이벤트를 활용해 미접속 유저의 복귀를 유도해 보는게 어떨까요? "
    ),
    "response_rate_within_24h": lambda m: (
        f"응답률이 {_percent_text(_to_float(m['response_rate_within_24h']))}입니다. " 
        "초기 응답 속도를 조금 더 높일 수 있습니다. "
        "무응답 글에 직접 답변을 달아 반응 흐름을 만들어 주세요. "
    ),
    "avg_comments_per_post": lambda m: (
        f"평균 댓글이 {_num_text(_to_float(m['avg_comments_per_post']))}개입니다. "
        "조금 더 확장될 여지가 있습니다. "
        "질문형 문구를 활용해 자연스럽게 댓글 참여를 유도해 주세요. "
    ),
    "new_user_settlement_rate": lambda m: (
        f"신규 정착률이 {_percent_text(_to_float(m['new_user_settlement_rate']))}입니다. "
        "신규 유저의 참여 동선을 조금 더 보완할 필요가 있습니다. "
        "신규 가입자에게 환영 메시지와 함께 가벼운 첫 미션을 안내해 보는게 어떨까요? "
    ),
}


def _weakest_info(metrics: dict[str, Any]) -> str:
    candidates: dict[str, float] = {
        "user_activation_rate": _safe_ratio(_to_float(metrics["user_activation_rate"]), INSIGHT_TARGET_ACTIVATION_RATE),
        "response_rate_within_24h": _safe_ratio(
            _to_float(metrics["response_rate_within_24h"]), INSIGHT_TARGET_RESPONSE_RATE
        ),
        "avg_comments_per_post": _safe_ratio(_to_float(metrics["avg_comments_per_post"]), INSIGHT_TARGET_AVG_COMMENTS),
    }

    if int(metrics["new_users_count"]) > 0:
        candidates["new_user_settlement_rate"] = _safe_ratio(
            _to_float(metrics["new_user_settlement_rate"]), INSIGHT_TARGET_SETTLEMENT_RATE
        )

    min_score = min(candidates.values()) if candidates else 0.0
    weakest = [k for k, v in candidates.items() if isclose(v, min_score, rel_tol=1e-9, abs_tol=1e-9)]

    weakest_key = next((key for key in INSIGHT_WEAKEST_TIEBREAK_ORDER if key in weakest), weakest[0])
    return WEAKEST_MESSAGE_BUILDERS[weakest_key](metrics)


def select_findings(metrics: dict[str, Any]) -> list[Finding]:
    selected_by_group: dict[str, Finding] = {}

    for rule in sorted(_build_rules(), key=lambda r: r.priority):
        if not rule.condition(metrics):
            continue
        if rule.group in selected_by_group:
            continue
        selected_by_group[rule.group] = {
            "rule_id": rule.rule_id,
            "group": rule.group,
            "priority": rule.priority,
            "level": rule.level,
            "title": rule.title,
            "message": rule.message(metrics),
        }

    return sorted(selected_by_group.values(), key=lambda item: item["priority"])


def resolve_overall_status(metrics: dict[str, Any], findings: list[Finding]) -> tuple[InsightLevel, list[Finding]]:
    critical_count = sum(1 for f in findings if f["level"] == "CRITICAL")
    warning_count = sum(1 for f in findings if f["level"] == "WARNING")

    if critical_count > 0:
        return "CRITICAL", findings

    if warning_count > 0:
        return "WARNING", findings

    if _is_good(metrics, critical_count, warning_count):
        return "GOOD", findings + [
            {
                "rule_id": "overall_good",
                "group": "overall",
                "priority": 999,
                "level": "GOOD",
                "title": "운영 양호",
                "message": "핵심 지표가 안정적입니다. 현재 운영 흐름을 유지해 주세요.",
            }
        ]

    prefix = "신규 가입자가 없습니다. " if int(metrics["new_users_count"]) == 0 else ""
    return "INFO", findings + [
        {
            "rule_id": "overall_info",
            "group": "overall",
            "priority": 999,
            "level": "INFO",
            "title": "운영 점검",
            "message": prefix + _weakest_info(metrics),
        }
    ]


def render_admin_lines(
    metrics: dict[str, Any],
    deltas: dict[str, Any],
    overall_status: InsightLevel,
    findings: list[Finding],
) -> tuple[str, str, list[Finding], int]:
    top_findings = findings[:2]
    remaining = max(len(findings) - len(top_findings), 0)

    summary_line = (
        "지표 요약 | "
        f"활성화율 {_percent_text(_to_float(metrics['user_activation_rate']))} "
        f"({deltas['user_activation_rate_delta']:+.2f}%p), "
        f"응답률 {_percent_text(_to_float(metrics['response_rate_within_24h']))} "
        f"({deltas['response_rate_within_24h_delta']:+.2f}%p), "
        f"댓글/글 {_num_text(_to_float(metrics['avg_comments_per_post']))} "
        f"({deltas['avg_comments_per_post_delta']:+.2f})"
    )

    verdict_line = (
        f"판정 | {overall_status} | "
        + ", ".join(f"{item['title']}({item['level']})" for item in top_findings)
        + (f" 외 {remaining}건" if remaining > 0 else "")
    )

    return summary_line, verdict_line, top_findings, remaining


def build_insight_report(metrics_result: dict[str, Any]) -> dict[str, Any]:
    metrics = metrics_result["current"]["metrics"]
    deltas = metrics_result["deltas"]

    findings = select_findings(metrics)
    overall_status, findings = resolve_overall_status(metrics, findings)
    summary_line, verdict_line, top_findings, _remaining = render_admin_lines(
        metrics=metrics,
        deltas=deltas,
        overall_status=overall_status,
        findings=findings,
    )

    return {
        "overall_status": overall_status,
        "findings": findings,
        "top_findings": top_findings,
        "summary_line": summary_line,
        "verdict_line": verdict_line,
    }
