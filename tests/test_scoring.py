"""Unit tests for the scoring engine."""
from paid_ad_optimizer.scoring import score_campaign
from paid_ad_optimizer.funnel import diagnose_funnel
from paid_ad_optimizer.benchmarks import get_benchmark
from conftest import make_brief, make_metrics


def _score(b, m):
    f = diagnose_funnel(b, m, get_benchmark(b.vertical))
    return score_campaign(b, m, get_benchmark(b.vertical), f), f


def test_band_is_letter():
    b = make_brief()
    m = make_metrics()
    sc, _ = _score(b, m)
    assert sc.band in {"A", "B", "C", "D", "F"}


def test_total_within_range():
    b = make_brief()
    sc, _ = _score(b, make_metrics())
    assert 0.0 <= sc.total <= 100.0


def test_weights_sum_to_one():
    b = make_brief()
    sc, _ = _score(b, make_metrics())
    assert abs(sum(d.weight for d in sc.dimensions) - 1.0) < 1e-9


def test_ltv_cac_computed_when_ltv_present():
    b = make_brief(ltv=120)
    m = make_metrics(conversions=110, spend=5000)  # cpa ~45.45
    sc, _ = _score(b, m)
    assert sc.ltv_cac_ratio is not None
    assert abs(sc.ltv_cac_ratio - (120 / (5000 / 110))) < 1e-6


def test_ltv_cac_none_without_ltv():
    b = make_brief(ltv=None)
    sc, _ = _score(b, make_metrics())
    assert sc.ltv_cac_ratio is None


def test_fatigue_propagates_to_scorecard():
    b = make_brief()
    m = make_metrics(frequency=9.0)
    sc, _ = _score(b, m)
    assert sc.fatigue is True


def test_economics_verdict_sustainable():
    b = make_brief(ltv=600)
    m = make_metrics(spend=1000, conversions=20)  # cpa 50, ltv/cpa 12
    sc, _ = _score(b, m)
    assert "sustainable" in sc.economics_verdict.lower()
