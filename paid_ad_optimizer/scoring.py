"""Scoring engine: weighted efficiency scorecard grounded in unit economics.

Dimensions and weights (total 100):
  - Economic efficiency (ROAS/CPA vs LTV)      30%
  - Targeting quality (overlap, relevance)     20%
  - Creative effectiveness (AIDA, CTR/CVR)      20%
  - Structure & budget allocation              15%
  - Measurement rigor (attribution)            15%
"""
from __future__ import annotations
from .models import (
    CampaignBrief, CampaignMetrics, VerticalBenchmark,
    Scorecard, DimensionScore, SignificanceResult,
)
from .significance import ab_significance

FREQUENCY_HARD_CEILING = 7.0


def _band(total: float) -> str:
    if total >= 85:
        return "A"
    if total >= 75:
        return "B"
    if total >= 65:
        return "C"
    if total >= 50:
        return "D"
    return "F"


def _clamp(x: float) -> float:
    return max(0.0, min(100.0, float(x)))


def _economics_score(brief: CampaignBrief, metrics: CampaignMetrics,
                     bench: VerticalBenchmark) -> tuple[float, str, str]:
    pts: list[float] = []
    rationale_bits: list[str] = []
    if metrics.conversions > 0:
        if brief.ltv and brief.ltv > 0:
            ratio = brief.ltv / metrics.cpa
            if ratio >= 3.0:
                pts.append(95.0); rationale_bits.append(
                    "LTV:CAC {:.1f}:1 is sustainable (>=3:1).".format(ratio))
            elif ratio >= 1.5:
                pts.append(65.0); rationale_bits.append(
                    "LTV:CAC {:.1f}:1 is marginal (target 3:1).".format(ratio))
            else:
                pts.append(20.0); rationale_bits.append(
                    "LTV:CAC {:.1f}:1 is unsustainable (<1.5:1, acquiring at a loss).".format(ratio))
        if brief.target_roas and metrics.roas >= brief.target_roas:
            pts.append(90.0); rationale_bits.append(
                "ROAS {:.2f} meets/exceeds target {:.2f}.".format(metrics.roas, brief.target_roas))
        elif brief.target_roas:
            pts.append(30.0); rationale_bits.append(
                "ROAS {:.2f} below target {:.2f}.".format(metrics.roas, brief.target_roas))
        if metrics.cpa <= bench.cpa_p75:
            pts.append(80.0); rationale_bits.append(
                "CPA {:.2f} <= vertical good ceiling {:.2f}.".format(metrics.cpa, bench.cpa_p75))
        elif metrics.cpa <= bench.cpa_p50:
            pts.append(60.0); rationale_bits.append(
                "CPA {:.2f} around median {:.2f}.".format(metrics.cpa, bench.cpa_p50))
        else:
            pts.append(25.0); rationale_bits.append(
                "CPA {:.2f} above vertical good ceiling {:.2f}.".format(metrics.cpa, bench.cpa_p75))
    else:
        pts.append(20.0); rationale_bits.append("Zero conversions recorded; economics unmeasurable.")
    score = _clamp(sum(pts) / len(pts)) if pts else 0.0
    return score, " ".join(rationale_bits), "Economics scored on CPA vs LTV/benchmark and ROAS vs target."


def _targeting_score(metrics: CampaignMetrics) -> tuple[float, str, str]:
    overlap = metrics.audience_overlap_pct
    if overlap < 15:
        return 90.0, "Audience overlap {:.0f}% is healthy (<15%).".format(overlap), "Low cannibalization risk."
    if overlap < 30:
        return 70.0, "Audience overlap {:.0f} is moderate; watch delivery waste.".format(overlap), "Moderate overlap."
    return 35.0, "Audience overlap {:.0f}% is high (>=30%); consolidate/exclude.".format(overlap), "High cannibalization."


def _creative_score(metrics: CampaignMetrics, bench: VerticalBenchmark,
                     funnel) -> tuple[float, str, str]:
    ctr_ratio = metrics.ctr / bench.ctr_median if bench.ctr_median else 0.0
    cvr_ratio = metrics.cvr / bench.cvr_median if bench.cvr_median else 0.0
    parts = [60.0 * min(1.5, ctr_ratio), 40.0 * min(1.5, cvr_ratio)]
    if funnel.fatigue:
        parts = [p * 0.6 for p in parts]
    score = _clamp(sum(parts))
    rationale = "CTR {:.0%} of benchmark, CVR {:.0%} of benchmark{}.".format(
        ctr_ratio, cvr_ratio, "; fatigue penalty applied" if funnel.fatigue else "")
    return score, rationale, "AIDA fit via CTR/CVR vs benchmark with fatigue penalty."


def _structure_score(metrics: CampaignMetrics) -> tuple[float, str, str]:
    score = 70.0
    if metrics.frequency > FREQUENCY_HARD_CEILING:
        score -= 20.0
    if metrics.impressions > 0 and metrics.cpm < 50.0:
        score += 10.0
    score = _clamp(score)
    return score, "CPM {:.2f}, frequency {:.1f}.".format(metrics.cpm, metrics.frequency), "Structure proxy via CPM/frequency."


def _measurement_score(metrics: CampaignMetrics, sig: SignificanceResult) -> tuple[float, str, str]:
    score = 50.0
    bits: list[str] = []
    if metrics.has_incrementality_holdout:
        score += 25.0; bits.append("incrementality holdout present")
    else:
        bits.append("no incrementality holdout; recommend geo-lift")
    if metrics.is_ab_test:
        if sig.is_significant:
            score += 15.0; bits.append("A/B significant")
        else:
            score -= 10.0; bits.append("A/B reported but not significant")
    score = _clamp(score)
    return score, "; ".join(bits) + ".", "Measurement rigor from attribution/test discipline."


def score_campaign(brief: CampaignBrief, metrics: CampaignMetrics,
                   bench: VerticalBenchmark, funnel) -> Scorecard:
    """Compute the full weighted scorecard plus economics verdict."""
    sig = ab_significance(metrics)

    econ_s, econ_r, econ_d = _economics_score(brief, metrics, bench)
    tgt_s, tgt_r, tgt_d = _targeting_score(metrics)
    cre_s, cre_r, cre_d = _creative_score(metrics, bench, funnel)
    str_s, str_r, str_d = _structure_score(metrics)
    mes_s, mes_r, mes_d = _measurement_score(metrics, sig)

    dims = (
        DimensionScore("Economic efficiency", 0.30, econ_s, econ_r, econ_d),
        DimensionScore("Targeting quality", 0.20, tgt_s, tgt_r, tgt_d),
        DimensionScore("Creative effectiveness", 0.20, cre_s, cre_r, cre_d),
        DimensionScore("Structure & budget allocation", 0.15, str_s, str_r, str_d),
        DimensionScore("Measurement rigor", 0.15, mes_s, mes_r, mes_d),
    )
    total = _clamp(sum(d.score * d.weight for d in dims))

    ltv_cac = (brief.ltv / metrics.cpa) if (brief.ltv and metrics.conversions > 0) else None
    if ltv_cac is None:
        eco_verdict = "LTV unknown; economics verdict requires LTV input."
    elif ltv_cac >= 3.0:
        eco_verdict = "Sustainable (LTV:CAC {:.1f}:1).".format(ltv_cac)
    elif ltv_cac >= 1.5:
        eco_verdict = "Marginal (LTV:CAC {:.1f}:1); push toward 3:1.".format(ltv_cac)
    else:
        eco_verdict = "Unsustainable (LTV:CAC {:.1f}:1); acquire cheaper or raise LTV.".format(ltv_cac)

    return Scorecard(
        dimensions=dims,
        total=total,
        band=_band(total),
        ltv_cac_ratio=ltv_cac,
        economics_verdict=eco_verdict,
        fatigue=funnel.fatigue,
        significance=sig,
    )
