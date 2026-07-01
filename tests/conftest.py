"""Shared fixtures and scenario builders for the test suite."""
from __future__ import annotations
import pytest
from paid_ad_optimizer.models import CampaignBrief, CampaignMetrics


def make_brief(**overrides) -> CampaignBrief:
    base = dict(
        platform="meta", objective="conversion", business_goal="Grow DTC sales",
        vertical="ecommerce", segments=("purchasers", "lookalike"),
        ltv=120, target_roas=2.5,
    )
    base.update(overrides)
    return CampaignBrief(**base)


def make_metrics(**overrides) -> CampaignMetrics:
    base = dict(
        spend=5000, impressions=400_000, clicks=5200, conversions=110,
        revenue=7200, frequency=8.0, audience_overlap_pct=42,
    )
    base.update(overrides)
    return CampaignMetrics(**base)


@pytest.fixture
def brief():
    return make_brief()


@pytest.fixture
def metrics():
    return make_metrics()


@pytest.fixture
def fatigue_metrics():
    return make_metrics(frequency=8.0, clicks=4800, conversions=110, revenue=6800)
