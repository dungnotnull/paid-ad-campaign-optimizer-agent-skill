"""Scenario tests: the 6 documented end-to-end scenarios in tests/test-scenarios.md.

Each scenario maps to one test that asserts the documented Pass criterion.
"""
import pytest
from paid_ad_optimizer import optimize, render_report
from paid_ad_optimizer.models import CampaignBrief, CampaignMetrics


def _run(b, m, creative="", terms=()):
    return optimize(b, m, creative_text=creative, targeting_terms=terms)


# Scenario 1 - Dropping ROAS diagnosis
def test_scenario_1_dropping_roas():
    b = CampaignBrief(platform="meta", objective="conversion",
                      business_goal="Grow DTC sales", vertical="ecommerce",
                      ltv=120, target_roas=3.0, segments=("purchasers",))
    m = CampaignMetrics(spend=5000, impressions=400_000, clicks=5200, conversions=110,
                        revenue=6800, frequency=8.0, audience_overlap_pct=12)
    r = _run(b, m)
    # leak identified (economics due to ROAS drop + fatigue evidence)
    assert r.funnel.leak_point == "economics"
    assert r.funnel.fatigue is True
    actions = [a.title for a in r.roadmap.actions]
    assert any("economics" in a.lower() or "unit economics" in a.lower() for a in actions)
    # each action states an expected effect
    assert all(a.expected_effect.strip() for a in r.roadmap.actions)


# Scenario 2 - Vanity-CTR trap
def test_scenario_2_vanity_ctr_trap():
    b = CampaignBrief(platform="google", objective="conversion",
                      business_goal="SaaS trial signups", vertical="saas",
                      ltv=400, target_roas=2.0)
    # high CTR (2%) but low CVR (0.3%) and very high CPA (333) vs LTV/3 (133)
    m = CampaignMetrics(spend=2000, impressions=100_000, clicks=2000, conversions=6,
                        revenue=1200, frequency=2.0, audience_overlap_pct=5)
    r = _run(b, m)
    # economics/landing wins; never celebrated on CTR
    assert r.funnel.leak_point in ("economics", "landing")
    assert r.scorecard.economics_verdict.lower().startswith("unsustainable")


# Scenario 3 - Creative fatigue
def test_scenario_3_creative_fatigue():
    b = CampaignBrief(platform="tiktok", objective="consideration",
                      business_goal="Brand video engagement", vertical="ecommerce",
                      segments=("broad-18-34",))
    m = CampaignMetrics(spend=3000, impressions=900_000, clicks=9000, conversions=120,
                        revenue=3000, frequency=8.0, audience_overlap_pct=8)
    r = _run(b, m)
    assert r.funnel.fatigue is True
    assert r.scorecard.fatigue is True
    assert any("refresh" in a.title.lower() or "creative" in a.title.lower()
               for a in r.roadmap.actions)


# Scenario 4 - Non-significant A/B test
def test_scenario_4_non_significant_ab():
    b = CampaignBrief(platform="meta", objective="conversion",
                      business_goal="Lead form submissions", vertical="lead-gen",
                      ltv=90, target_roas=1.8)
    m = CampaignMetrics(spend=2000, impressions=200_000, clicks=3000, conversions=40,
                        revenue=3000, frequency=3.0, is_ab_test=True,
                        ab_control_conversions=18, ab_control_visitors=2000,
                        ab_variant_conversions=22, ab_variant_visitors=2000)
    r = _run(b, m)
    sig = r.scorecard.significance
    assert sig is not None
    assert sig.is_significant is False
    assert "insufficient" in sig.verdict.lower() or "not significant" in sig.verdict.lower()


# Scenario 5 - Prohibited health claim (compliance)
def test_scenario_5_prohibited_health_claim():
    b = CampaignBrief(platform="meta", objective="conversion",
                      business_goal="Sell supplement", vertical="health",
                      segments=("wellness-interest",))
    m = CampaignMetrics(spend=1000, impressions=80_000, clicks=1200, conversions=20,
                        revenue=1800, frequency=3.0)
    r = _run(b, m, creative="Our supplement cures diabetes - guaranteed results in 7 days!")
    assert r.compliance.verdict == "Fail"
    assert r.compliance.blocking is True
    assert r.roadmap.actions[0].lever == "compliance"


# Scenario 6 - Offline / degraded mode
def test_scenario_6_offline_degraded(tmp_path, monkeypatch):
    from paid_ad_optimizer import knowledge
    # point brain at a non-existent file to force offline/degraded detection
    fake = tmp_path / "no-brain.md"
    b = CampaignBrief(platform="meta", objective="conversion",
                      business_goal="Grow DTC sales", vertical="ecommerce", ltv=120)
    m = CampaignMetrics(spend=1000, impressions=100_000, clicks=1500, conversions=60,
                        revenue=3500, frequency=2.0)
    r = optimize(b, m, knowledge_path=fake)
    assert r.offline is True
    report = render_report(r)
    assert "offline" in report.lower()
    assert "refresh" in report.lower() and "knowledge_updater" in report.lower()
