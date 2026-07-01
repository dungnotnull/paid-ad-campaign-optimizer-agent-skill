"""Improvement roadmap generator.

Converts the scorecard, funnel diagnosis, and compliance fixes into a ranked,
prioritized list of actions. Each action states an expected effect, a
confidence level, an effort tag, and an impact tag. Compliance fixes are always
included first and non-optional (no Fail item passes unresolved). The roadmap
always appends a measurement/incrementality plan.
"""
from __future__ import annotations
from .models import (
    CampaignBrief, CampaignMetrics, Scorecard, FunnelDiagnosis,
    ComplianceVerdict, Roadmap, RoadmapAction,
)

_LEVER_BY_LEAK = {
    "economics": "budget",
    "landing": "creative",
    "offer": "creative",
    "creative": "creative",
    "targeting": "targeting",
    "none": "measurement",
}


def _effort_impact(confidence: str, funnel_impact: str) -> tuple[str, str]:
    eff = {"high": "S", "med": "M", "low": "L"}.get(confidence, "M")
    return eff, funnel_impact


def _leak_actions(brief: CampaignBrief, metrics: CampaignMetrics,
                  funnel: FunnelDiagnosis, bench) -> list[RoadmapAction]:
    actions: list[RoadmapAction] = []
    leak = funnel.leak_point
    if leak == "creative" or funnel.fatigue:
        actions.append(RoadmapAction(
            priority=1, title="Refresh creative & expand audience",
            lever="creative",
            action="Introduce 3-5 new creative variants; retire fatigued assets "
                   "(frequency >= {:.1f}); expand to lookalikes to reset frequency.".format(
                       bench.frequency_fatigue),
            expected_effect="Restore CTR toward benchmark (~{:+.0%} vs current); "
                            "lower frequency and ~15-25% CPA reduction.".format(
                                max(-0.25, 1.0 - funnel.ctr_vs_benchmark)),
            confidence="med", effort="M", impact="High",
            measurement="Holdout one creative cohort vs control for 2 weeks; measure CTR delta.",
        ))
    if leak == "targeting":
        actions.append(RoadmapAction(
            priority=1, title="Refine targeting fit",
            lever="targeting",
            action="Tighten audience to high-intent behaviors; exclude converters; "
                   "split broad vs interest stacks.",
            expected_effect="CTR +{:.0%} toward benchmark; lower waste and overlap.".format(
                1.0 - funnel.ctr_vs_benchmark),
            confidence="med", effort="M", impact="High",
            measurement="A/B test refined vs current targeting; require significance before scaling.",
        ))
    if leak in ("landing", "offer"):
        actions.append(RoadmapAction(
            priority=1, title="Fix landing/offer to lift CVR",
            lever="creative",
            action="Audit landing page vs creative promise; test offer, headline, "
                   "and form length; ensure mobile-first load <2.5s.",
            expected_effect="CVR +{:.0%} toward benchmark; CPA falls proportionally.".format(
                1.0 - funnel.cvr_vs_benchmark),
            confidence="high", effort="M", impact="High",
            measurement="A/B landing variants; ~{:.0f} conversions/arm required.".format(
                max(100, 0)),
        ))
    if leak == "economics":
        actions.append(RoadmapAction(
            priority=1, title="Restore unit economics",
            lever="budget",
            action="Shift spend to the segments with the best CPA/ROAS; pause "
                   "loss-making ad sets; raise LTV via retention bundles or trim CPM bids.",
            expected_effect="Move LTV:CAC toward >=3:1; cut CPA toward <= {:.2f}.".format(
                (brief.ltv / 3.0) if brief.ltv else bench.cpa_p75),
            confidence="med", effort="L", impact="High",
            measurement="Track blended CPA vs LTV/3 weekly; geo-lift to confirm incrementality.",
        ))
    if leak == "none":
        actions.append(RoadmapAction(
            priority=2, title="Scale winners with a measurement plan",
            lever="budget",
            action="Scale the best ad sets incrementally (+20% budget/week) while "
                   "watching CPA; add an incrementality holdout.",
            expected_effect="Grow profitable volume without breaking CPA economics.",
            confidence="high", effort="S", impact="Med",
            measurement="Geo-lift holdout; stop scaling if incremental CPA exceeds LTV/3.",
        ))
    # Targeting overlap action whenever overlap is high, regardless of leak.
    if metrics.audience_overlap_pct >= 30 and not any(
            a.lever == "targeting" for a in actions):
        actions.append(RoadmapAction(
            priority=2, title="Consolidate overlapping audiences",
            lever="targeting",
            action="Merge/convert overlapping ad sets; use exclusions to stop "
                   "self-competition.",
            expected_effect="Reduce overlap {:.0f}% -> <15%; lower CPM and wasted reach.".format(
                metrics.audience_overlap_pct),
            confidence="high", effort="S", impact="Med",
            measurement="Compare CPM and frequency before/after consolidation.",
        ))
    return actions


def _compliance_actions(verdict: ComplianceVerdict) -> list[RoadmapAction]:
    out: list[RoadmapAction] = []
    for i, f in enumerate(verdict.findings, start=1):
        if f.severity in ("fail", "conditional"):
            out.append(RoadmapAction(
                priority=0,
                title="Compliance fix #{}: {}".format(i, f.rule),
                lever="compliance",
                action=f.required_fix,
                expected_effect="Unblocks publication; avoids ad rejection and legal risk.",
                confidence="high",
                effort="S" if f.severity == "fail" else "M",
                impact="High" if f.severity == "fail" else "Med",
                measurement="Re-run compliance check; require Pass before scaling.",
            ))
    return out


def build_roadmap(brief: CampaignBrief, metrics: CampaignMetrics,
                  scorecard: Scorecard, funnel: FunnelDiagnosis,
                  compliance: ComplianceVerdict, bench) -> Roadmap:
    """Assemble the prioritized roadmap: compliance-first, then leak-driven,
    then structural/measurement actions."""
    actions: list[RoadmapAction] = []
    actions.extend(_compliance_actions(compliance))
    actions.extend(_leak_actions(brief, metrics, funnel, bench))

    # Measurement rigor action (always present per the measurement-plan gate).
    actions.append(RoadmapAction(
        priority=3,
        title="Stand up incrementality measurement",
        lever="measurement",
        action="Run a geo-lift holdout (or PSA-based holdout for retention) to "
               "measure true incremental contribution; report incremental ROAS vs "
               "platform-reported ROAS.",
        expected_effect="Separate true effect from attribution noise; protect budget "
                        "from over-crediting paid.",
        confidence="high", effort="L", impact="High",
        measurement="4-6 week holdout; significance threshold p<0.05; minimum ~{:.0f} "
                     "conversions per geo cell.".format(100),
    ))

    # De-duplicate by (lever, action) and renumber priorities deterministically.
    seen = set()
    deduped: list[RoadmapAction] = []
    for a in actions:
        key = (a.lever, a.action)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(a)
    # Sort: compliance (priority 0) first, then by priority, then by impact.
    impact_rank = {"High": 0, "Med": 1, "Low": 2}
    deduped.sort(key=lambda a: (a.priority, impact_rank.get(a.impact, 1), a.title))
    final = tuple(RoadmapAction(
        priority=i, title=a.title, lever=a.lever, action=a.action,
        expected_effect=a.expected_effect, confidence=a.confidence,
        effort=a.effort, impact=a.impact, measurement=a.measurement,
    ) for i, a in enumerate(deduped, start=1))

    plan = (
        "Measurement plan: (1) instrument a geo-lift/PSA holdout for the top "
        "budget ad set; (2) pre-register A/B tests with the required conversion "
        "floor (~{:.0f}/arm) before declaring winners; (3) report incremental ROAS "
        "alongside platform ROAS; (4) refresh benchmarks weekly via "
        "tools/knowledge_updater.py.".format(100)
    )
    return Roadmap(
        actions=final,
        measurement_plan=plan,
        compliance_fixes_included=any(a.lever == "compliance" for a in final),
    )
