"""Unit tests for models: validation and derived metrics."""
import math
import pytest
from paid_ad_optimizer.models import CampaignBrief, CampaignMetrics


def test_brief_validates_objective():
    with pytest.raises(ValueError):
        CampaignBrief(platform="meta", objective="engagement",
                      business_goal="x", vertical="ecommerce").validate()


def test_brief_validates_platform():
    with pytest.raises(ValueError):
        CampaignBrief(platform="snap", objective="conversion",
                      business_goal="x", vertical="ecommerce").validate()


def test_brief_requires_goal_and_vertical():
    with pytest.raises(ValueError):
        CampaignBrief(platform="meta", objective="conversion",
                      business_goal="", vertical="ecommerce").validate()
    with pytest.raises(ValueError):
        CampaignBrief(platform="meta", objective="conversion",
                      business_goal="x", vertical="").validate()


def test_metrics_derived_properties():
    m = CampaignMetrics(spend=1000, impressions=200_000, clicks=4000,
                         conversions=80, revenue=3000, frequency=5.0)
    assert abs(m.ctr - 0.02) < 1e-9
    assert abs(m.cvr - 0.02) < 1e-9
    assert abs(m.cpa - 12.5) < 1e-9
    assert abs(m.roas - 3.0) < 1e-9
    assert abs(m.cpm - 5.0) < 1e-9


def test_metrics_zero_safety():
    m = CampaignMetrics(spend=0, impressions=0, clicks=0, conversions=0)
    assert m.ctr == 0.0
    assert math.isinf(m.cpa)
    assert m.roas == 0.0


def test_metrics_validates_overlap_range():
    with pytest.raises(ValueError):
        CampaignMetrics(spend=10, impressions=10, clicks=1, conversions=1,
                        audience_overlap_pct=150).validate()
    with pytest.raises(ValueError):
        CampaignMetrics(spend=10, impressions=10, clicks=1, conversions=1,
                        frequency=-1).validate()


def test_optreport_json_roundtrip(brief, metrics):
    from paid_ad_optimizer import optimize
    r = optimize(brief, metrics)
    s = r.to_json()
    import json
    d = json.loads(s)
    assert d["brief"]["platform"] == "meta"
    assert "scorecard" in d
    assert "compliance" in d
    assert "roadmap" in d
