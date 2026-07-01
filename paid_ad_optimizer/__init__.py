"""paid_ad_optimizer — Paid Ad Campaign Optimizer engine package.

Production-grade, dependency-light Python implementation of the
paid-ad-campaign-optimizer skill harness: audience analysis, funnel
diagnosis, statistical A/B significance, weighted efficiency scoring,
ad-policy compliance, and prioritized optimization roadmaps, grounded in
unit economics (ROAS / CPA vs LTV) and dated per-vertical benchmarks.

Public API:
    from paid_ad_optimizer import (
        CampaignBrief, CampaignMetrics, VerticalBenchmark, Scorecard,
        ComplianceVerdict, Roadmap, optimize,
        audience_analysis, diagnose_funnel, ab_significance,
        score_campaign, check_compliance, build_roadmap,
    )
"""
from .models import (
    CampaignBrief, CampaignMetrics, VerticalBenchmark, AudienceAnalysis,
    FunnelDiagnosis, SignificanceResult, DimensionScore, Scorecard,
    ComplianceFinding, ComplianceVerdict, RoadmapAction, Roadmap, OptReport,
)
from .benchmarks import BENCHMARKS, get_benchmark, benchmark_currency
from .audience import audience_analysis
from .funnel import diagnose_funnel
from .significance import ab_significance, required_sample_size
from .scoring import score_campaign
from .compliance import check_compliance
from .roadmap import build_roadmap
from .knowledge import KnowledgeBrain
from .pipeline import optimize, render_report

__all__ = [
    "CampaignBrief", "CampaignMetrics", "VerticalBenchmark", "AudienceAnalysis",
    "FunnelDiagnosis", "SignificanceResult", "DimensionScore", "Scorecard",
    "ComplianceFinding", "ComplianceVerdict", "RoadmapAction", "Roadmap",
    "OptReport", "BENCHMARKS", "get_benchmark", "benchmark_currency",
    "audience_analysis", "diagnose_funnel", "ab_significance",
    "required_sample_size", "score_campaign", "check_compliance",
    "build_roadmap", "KnowledgeBrain", "optimize", "render_report",
]

__version__ = "1.0.0"
