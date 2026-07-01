"""Unit tests for audience analysis + the objective/KPI gate."""
import pytest
from paid_ad_optimizer.audience import audience_analysis
from conftest import make_brief, make_metrics


def test_conversion_objective_maps_to_cpa():
    b = make_brief(objective="conversion")
    a = audience_analysis(b, make_metrics())
    assert a.primary_kpi == "cpa"
    assert a.objective == "conversion"


def test_awareness_objective_maps_to_reach():
    b = make_brief(objective="awareness")
    a = audience_analysis(b, make_metrics())
    assert a.primary_kpi == "reach"


def test_consideration_objective_maps_to_ctr():
    b = make_brief(objective="consideration")
    a = audience_analysis(b, make_metrics())
    assert a.primary_kpi == "ctr"


def test_high_overlap_is_flagged():
    a = audience_analysis(make_brief(), make_metrics(audience_overlap_pct=55))
    assert "cannibalization" in a.notes.lower()
    assert a.overlap_pct == 55.0


def test_unsustainable_target_cpa_flagged():
    b = make_brief(ltv=120, target_cpa=80)  # LTV/3 = 40, target 80 > 40
    a = audience_analysis(b, make_metrics())
    assert "unsustainable" in a.notes.lower()


def test_unknown_objective_raises():
    with pytest.raises(ValueError):
        audience_analysis(make_brief(objective="engagement"), make_metrics())


def test_segments_default_when_empty():
    a = audience_analysis(make_brief(segments=()), make_metrics())
    assert a.segments == ("all-users",)
