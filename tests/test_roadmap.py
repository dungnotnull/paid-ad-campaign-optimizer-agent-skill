"""Unit tests for the roadmap builder."""
from paid_ad_optimizer.roadmap import build_roadmap
from paid_ad_optimizer.scoring import score_campaign
from paid_ad_optimizer.funnel import diagnose_funnel
from paid_ad_optimizer.compliance import check_compliance
from paid_ad_optimizer.benchmarks import get_benchmark
from conftest import make_brief, make_metrics


def _roadmap(b, m, creative="", terms=()):
    bench = get_benchmark(b.vertical)
    f = diagnose_funnel(b, m, bench)
    sc = score_campaign(b, m, bench, f)
    comp = check_compliance(b, m, creative, terms)
    return build_roadmap(b, m, sc, f, comp, bench)


def test_every_action_has_expected_effect():
    r = _roadmap(make_brief(), make_metrics(frequency=8.0))
    for a in r.actions:
        assert a.expected_effect.strip() != ""
        assert a.lever in {"budget", "targeting", "creative", "structure", "measurement", "compliance"}


def test_compliance_fixes_first_when_fail():
    r = _roadmap(make_brief(vertical="health"),
                make_metrics(),
                creative="Cures diabetes guaranteed")
    assert r.compliance_fixes_included is True
    assert r.actions[0].lever == "compliance"


def test_measurement_action_always_present():
    r = _roadmap(make_brief(ltv=200, target_roas=2.0),
                make_metrics(spend=1000, impressions=100_000, clicks=1500,
                             conversions=60, revenue=3500, frequency=1.8,
                             audience_overlap_pct=5))
    assert any(a.lever == "measurement" for a in r.actions)


def test_actions_have_priority_order():
    r = _roadmap(make_brief(), make_metrics(frequency=8.0, audience_overlap_pct=45),
                creative="best product guaranteed")
    priorities = [a.priority for a in r.actions]
    assert priorities == sorted(priorities)
    assert priorities[0] == 1


def test_measurement_plan_present():
    r = _roadmap(make_brief(), make_metrics())
    assert "incrementality" in r.measurement_plan.lower() or "holdout" in r.measurement_plan.lower()
