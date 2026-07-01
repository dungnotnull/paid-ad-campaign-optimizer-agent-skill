"""Funnel diagnosis: pinpoint where the campaign leaks.

Maps the AIDA funnel + unit economics into a single leak-point verdict so the
roadmap can address the highest-leverage cause first. The engine never
celebrates vanity CTR when CVR/CPA are broken; it always anchors on economics.
"""
from __future__ import annotations
from .models import CampaignBrief, CampaignMetrics, VerticalBenchmark, FunnelDiagnosis


def _ratio(value: float, anchor: float) -> float:
    return value / anchor if anchor else 0.0


def diagnose_funnel(brief: CampaignBrief, metrics: CampaignMetrics,
                    bench: VerticalBenchmark) -> FunnelDiagnosis:
    """Diagnose the dominant leak point among creative / targeting / landing /
    offer / economics, plus creative-fatigue detection."""
    ctr = metrics.ctr
    cvr = metrics.cvr
    cpa = metrics.cpa
    roas = metrics.roas

    ctr_ratio = _ratio(ctr, bench.ctr_median)
    cvr_ratio = _ratio(cvr, bench.cvr_median)
    fatigue = metrics.frequency >= bench.frequency_fatigue

    notes: list[str] = []
    if fatigue:
        notes.append(
            "Creative fatigue likely: frequency {:.1f} >= {:.1f} fatigue "
            "threshold; CTR declining is the expected signature.".format(
                metrics.frequency, bench.frequency_fatigue)
        )
    if metrics.audience_overlap_pct >= 30.0:
        notes.append(
            "Audience overlap {:.0f}% >= 30%; targeting is wasteful and "
            "cannibalizing delivery.".format(metrics.audience_overlap_pct)
        )

    # Economics gate: CPA vs LTV/target, ROAS vs floor.
    economics_broken = False
    if brief.ltv and metrics.conversions > 0 and cpa > brief.ltv / 3.0:
        economics_broken = True
        notes.append(
            "CPA {:.2f} exceeds LTV/3 ({:.2f}); acquiring at a loss.".format(
                cpa, brief.ltv / 3.0)
        )
    if brief.target_roas and roas < brief.target_roas:
        economics_broken = True
        notes.append(
            "ROAS {:.2f} below target {:.2f}.".format(roas, brief.target_roas)
        )
    if metrics.conversions > 0 and roas < bench.roas_floor:
        economics_broken = True
        notes.append(
            "ROAS {:.2f} below vertical break-even floor {:.2f}.".format(
                roas, bench.roas_floor)
        )

    # Decide the dominant leak point by hierarchy: economics > landing/offer
    # (low CVR) > creative/targeting (low CTR). Economics wins because a
    # profitable funnel with bad CTR is still fixable; an unprofitable funnel
    # is unfixable by media tactics alone.
    if economics_broken:
        leak = "economics"
        evidence = "Unit economics breached: CPA/ROAS below sustainability thresholds."
    elif cvr_ratio < 0.5 and metrics.clicks > 0:
        leak = "landing"
        evidence = (
            "CVR {:.2%} is {:.0%} of the vertical benchmark {:.2%}; clicks arrive "
            "but do not convert. Inspect landing page, offer and price.".format(
                cvr, cvr_ratio, bench.cvr_median)
        )
    elif cvr_ratio < 0.75 and metrics.clicks > 0:
        leak = "offer"
        evidence = (
            "CVR {:.2%} is {:.0%} of benchmark; offer/value proposition likely "
            "underperforming, not a pure creative problem.".format(cvr, cvr_ratio)
        )
    elif ctr_ratio < 0.5 and metrics.impressions > 0:
        leak = "creative" if not fatigue else "targeting"
        evidence = (
            "CTR {:.2%} is {:.0%} of benchmark {:.2%}; {} is the bottleneck.".format(
                ctr, ctr_ratio, bench.ctr_median,
                "creative fatigue" if fatigue else "weak creative/targeting fit")
        )
    elif fatigue:
        leak = "creative"
        evidence = (
            "Frequency {:.1f} is at/above fatigue threshold; creative is worn out "
            "even though current CTR is acceptable.".format(metrics.frequency)
        )
    else:
        leak = "none"
        evidence = (
            "No dominant leak: CTR/CVR near benchmark and economics intact. "
            "Focus on incremental scale and measurement rigor."
        )

    return FunnelDiagnosis(
        leak_point=leak,
        evidence=evidence,
        fatigue=fatigue,
        fatigue_frequency=metrics.frequency,
        ctr_vs_benchmark=ctr_ratio,
        cvr_vs_benchmark=cvr_ratio,
        notes=tuple(notes),
    )
