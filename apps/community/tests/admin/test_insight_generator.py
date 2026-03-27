from django.test import SimpleTestCase

from apps.community.insights.insight_generator import build_insight_report


class CommunityInsightGeneratorTest(SimpleTestCase):
    def _payload(
        self,
        *,
        response: float = 65.0,
        settlement: float = 50.0,
        new_users: int = 1,
        comments: float = 1.6,
        likes: float = 0.8,
        activation: float = 12.0,
        top1: float = 50.0,
    ) -> dict[str, object]:
        return {
            "current": {
                "metrics": {
                    "user_activation_rate": activation,
                    "new_user_settlement_rate": settlement,
                    "new_users_count": new_users,
                    "avg_comments_per_post": comments,
                    "avg_likes_per_post": likes,
                    "response_rate_within_24h": response,
                    "active_category_post_counts": {"A": 3, "B": 2},
                    "top1_category_share": top1,
                }
            },
            "deltas": {
                "user_activation_rate_delta": 0.0,
                "response_rate_within_24h_delta": 0.0,
                "avg_comments_per_post_delta": 0.0,
            },
        }

    def test_same_group_selects_stronger_rule_only(self) -> None:
        """같은 룰 그룹에서는 더 강한 규칙 1개만 채택되는지 검증"""
        payload = self._payload(response=10.0, top1=50.0)
        report = build_insight_report(payload)

        response_findings = [f for f in report["findings"] if f["group"] == "response_rate"]
        self.assertEqual(len(response_findings), 1)
        self.assertEqual(response_findings[0]["rule_id"], "response_critical")

    def test_multi_group_can_be_shown_together(self) -> None:
        """서로 다른 룰 그룹의 이슈는 동시에 노출될 수 있는지 검증"""
        payload = self._payload(response=10.0, top1=90.0)
        report = build_insight_report(payload)

        groups = {f["group"] for f in report["findings"]}
        self.assertIn("response_rate", groups)
        self.assertIn("category_skew", groups)
        self.assertEqual(report["overall_status"], "CRITICAL")

    def test_warning_blocks_good(self) -> None:
        """WARNING이 하나라도 있으면 GOOD으로 판정되지 않는지 검증"""
        payload = self._payload(
            response=35.0,   # WARNING(<40, >=20)
            comments=2.0,
            activation=20.0,
            new_users=0,    # core 3/4 가능해도 WARNING 존재 시 GOOD 금지
            top1=50.0,
        )
        report = build_insight_report(payload)
        self.assertEqual(report["overall_status"], "WARNING")
        self.assertTrue(any(f["rule_id"] == "response_warning" for f in report["findings"]))

    def test_good_when_no_warning_and_core_3_of_4(self) -> None:
        """WARNING/CRITICAL이 없고 + 코어 조건 3/4 충족 시 GOOD 판정되는지 검증"""
        payload = self._payload(
            response=65.0,
            comments=1.6,
            activation=10.0,
            new_users=0,  # settlement 조건 자동 충족
            top1=50.0,
        )
        report = build_insight_report(payload)
        self.assertEqual(report["overall_status"], "GOOD")
        self.assertTrue(any(f["rule_id"] == "overall_good" for f in report["findings"]))

    def test_info_fallback_with_prefix_and_tiebreak(self) -> None:
        """fallback INFO 메시지의 접두어(new_users=0)와 동률 tie-break 우선순위 검증"""
        payload = self._payload(
            response=45.0,  # target 60 대비 0.75
            activation=11.25,  # target 15 대비 0.75 (동률)
            comments=1.4,  # target 1.5 대비 0.93
            likes=0.8,  # warning 아님
            new_users=0,  # settlement 후보 제외 + prefix
            top1=50.0,
        )
        report = build_insight_report(payload)

        self.assertEqual(report["overall_status"], "INFO")
        info = next(f for f in report["findings"] if f["rule_id"] == "overall_info")
        self.assertIn("신규 가입자가 없습니다.", info["message"])
        self.assertIn("응답률이 45.0%", info["message"])  # 동률이면 tie-break 순서상 response가 우선
