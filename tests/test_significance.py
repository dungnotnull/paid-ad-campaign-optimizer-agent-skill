"""Unit tests for A/B significance + required sample size."""
from paid_ad_optimizer.significance import ab_significance, required_sample_size
from paid_ad_optimizer.models import CampaignMetrics


def _ab(c_conv, c_vis, v_conv, v_vis):
    return CampaignMetrics(spend=0, impressions=0, clicks=0, conversions=0,
                           is_ab_test=True, ab_control_conversions=c_conv,
                           ab_control_visitors=c_vis,
                           ab_variant_conversions=v_conv,
                           ab_variant_visitors=v_vis)


def test_non_significant_low_volume_is_flagged():
    # 30 total conversions claimed as a 5% winner -> must NOT be significant
    m = _ab(15, 1000, 18, 1000)
    r = ab_significance(m)
    assert r.is_significant is False
    assert "insufficient" in r.verdict.lower() or "not significant" in r.verdict.lower()


def test_significant_with_adequate_volume():
    # control 1000/50000 (2%), variant 1250/50000 (2.5%) -> significant, large n
    m = _ab(1000, 50_000, 1250, 50_000)
    r = ab_significance(m)
    assert r.is_significant is True
    assert r.p_value < 0.05


def test_no_ab_test_returns_inert():
    m = CampaignMetrics(spend=10, impressions=100, clicks=10, conversions=1)
    r = ab_significance(m)
    assert r.is_significant is False
    assert "no a/b test" in r.verdict.lower()


def test_zero_visitors_handled():
    m = _ab(5, 0, 5, 1000)
    r = ab_significance(m)
    assert r.is_significant is False


def test_required_sample_size_sensible():
    n = required_sample_size(0.02, mde=0.10)
    # baseline 2%, MDE 10% relative -> need a meaningful number of visitors
    assert n >= 100


def test_equal_arms_not_significant():
    m = _ab(100, 10_000, 100, 10_000)
    r = ab_significance(m)
    assert r.is_significant is False
