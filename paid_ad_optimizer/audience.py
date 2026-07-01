"""Audience analysis sub-skill engine.

Maps the campaign objective to the correct primary KPI, captures LTV/AOV for
economics-based judging, and flags audience-segment overlap/cannibalization.
Gate: objective and primary KPI must be explicit; raises otherwise.
"""
from __future__ import annotations
from .models import CampaignBrief, CampaignMetrics, AudienceAnalysis

# objective -> (primary KPI, awareness-side KPI aliases used as guardrails)
_KPI_BY_OBJECTIVE = {
    "awareness": ("reach", ("cpm", "frequency", "recall")),
    "consideration": ("ctr", ("cpc", "engagement_rate", "video_view_rate")),
    "conversion": ("cpa", ("roas", "cvr", "ltv_cac")),
}


def _infer_overlap(metrics: CampaignMetrics) -> float:
    return float(max(0.0, min(100.0, metrics.audience_overlap_pct)))


def audience_analysis(brief: CampaignBrief, metrics: CampaignMetrics) -> AudienceAnalysis:
    """Produce an AudienceAnalysis; enforce the objective + KPI gate.

    Raises ValueError when objective is unknown or no business goal is set.
    """
    brief.validate()
    if brief.objective not in _KPI_BY_OBJECTIVE:
        raise ValueError("unknown objective: " + repr(brief.objective))

    primary_kpi, guardrails = _KPI_BY_OBJECTIVE[brief.objective]
    segments = tuple(s.strip() for s in brief.segments if s and s.strip())
    overlap = _infer_overlap(metrics)
    notes_bits = []
    if overlap >= 30.0:
        notes_bits.append(
            "High audience overlap ({:.0f}%) risks cannibalization; consolidate or "
            "exclude overlapping audiences.".format(overlap)
        )
    if brief.ltv is not None and brief.target_cpa is not None and brief.ltv > 0:
        if brief.target_cpa > brief.ltv / 3.0:
            notes_bits.append(
                "target_cpa ({:.2f}) exceeds LTV/3 ({:.2f}); "
                "unit economics unsustainable at this CPA target.".format(
                    brief.target_cpa, brief.ltv / 3.0)
            )
    notes_bits.append("Guardrail KPIs for {}: {}.".format(brief.objective, ", ".join(guardrails)))
    return AudienceAnalysis(
        objective=brief.objective,
        primary_kpi=primary_kpi,
        segments=segments if segments else ("all-users",),
        ltv=brief.ltv,
        aov=brief.aov,
        overlap_pct=overlap,
        notes=" ".join(notes_bits),
    )
