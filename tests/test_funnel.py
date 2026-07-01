"""Unit tests for funnel diagnosis."""
from paid_ad_optimizer.funnel import diagnose_funnel
from paid_ad_optimizer.benchmarks import get_benchmark
from conftest import make_brief, make_metrics


def test_economics_leak_when_roas_below_floor():
    b = make_brief(ltv=120, target_roas=3.0)
    m = make_metrics(spend=5000, impressions=400_000, clicks=5200,
                     conversions=110, revenue=6800, frequency=2.0,
                     audience_overlap_pct=10)
    f = diagnose_funnel(b, m, get_benchmark("ecommerce"))
    assert f.leak_point == "economics"


def test_creative_leak_when_low_ctr_no_fatigue():
    b = make_brief(vertical="ecommerce")
    m = make_metrics(spend=500, impressions=1_000_000, clicks=2000,
                     conversions=120, revenue=4000, frequency=1.5,
                     audience_overlap_pct=5)
    f = diagnose_funnel(b, m, get_benchmark("ecommerce"))
    # CTR 0.2% << benchmark 1.15% -> creative leak
    assert f.leak_point in ("creative", "targeting")
    assert f.ctr_vs_benchmark < 0.5


def test_landing_leak_when_low_cvr_but_ok_ctr():
    # Profitable economics (ltv=600, roas=2.5 >= target 2.0 and floor 2.0)
    # so the only leak is a low CVR relative to the vertical benchmark.
    b = make_brief(vertical="ecommerce", ltv=600, target_roas=2.0)
    m = make_metrics(spend=1000, impressions=100_000, clicks=1150,
                     conversions=6, revenue=2500, frequency=2.0,
                     audience_overlap_pct=5)
    f = diagnose_funnel(b, m, get_benchmark("ecommerce"))
    assert f.leak_point == "landing"


def test_fatigue_detected():
    b = make_brief()
    m = make_metrics(frequency=9.0, audience_overlap_pct=5)
    f = diagnose_funnel(b, m, get_benchmark("ecommerce"))
    assert f.fatigue is True


def test_no_leak_when_healthy():
    b = make_brief(ltv=200, target_roas=2.0)
    m = make_metrics(spend=1000, impressions=100_000, clicks=1500,
                     conversions=60, revenue=3500, frequency=1.8,
                     audience_overlap_pct=5)
    f = diagnose_funnel(b, m, get_benchmark("ecommerce"))
    assert f.leak_point == "none"


def test_offline_fallback_vertical():
    f = diagnose_funnel(make_brief(vertical="nonexistent-vertical"),
                        make_metrics(), get_benchmark("nonexistent-vertical"))
    # falls back to 'other' benchmark without error
    assert f.leak_point in ("economics", "none", "landing", "creative", "targeting", "offer")
