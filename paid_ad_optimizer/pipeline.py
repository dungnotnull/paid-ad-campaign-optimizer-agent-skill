"""Pipeline: orchestrate the full paid-ad-campaign-optimizer harness.

optimize() runs the six-stage flow end-to-end and returns an OptReport.
render_report() turns an OptReport into the markdown report the skill emits.
This is the programmatic equivalent of the agent skill described in
skills/main.md; both share the same quality gates.
"""
from __future__ import annotations
from .models import (
    CampaignBrief, CampaignMetrics, OptReport,
)
from .benchmarks import get_benchmark, benchmark_currency
from .audience import audience_analysis
from .funnel import diagnose_funnel
from .scoring import score_campaign
from .compliance import check_compliance
from .roadmap import build_roadmap
from .knowledge import load_brain


def optimize(brief: CampaignBrief, metrics: CampaignMetrics,
             creative_text: str = "", targeting_terms: tuple[str, ...] = (),
             knowledge_path=None) -> OptReport:
    """Run the full harness. Validates inputs and enforces all quality gates."""
    brief.validate()
    metrics.validate()

    bench = get_benchmark(brief.vertical)
    aud = audience_analysis(brief, metrics)
    funnel = diagnose_funnel(brief, metrics, bench)
    scorecard = score_campaign(brief, metrics, bench, funnel)
    compliance = check_compliance(brief, metrics, creative_text, targeting_terms)
    roadmap = build_roadmap(brief, metrics, scorecard, funnel, compliance, bench)

    kb = load_brain(knowledge_path)
    offline = not kb.exists or kb.is_stale()
    if offline:
        # Surface the limitation in the audience notes channel is already done;
        # here we just record it on the report.
        pass

    return OptReport(
        brief=brief,
        metrics=metrics,
        audience=aud,
        funnel=funnel,
        scorecard=scorecard,
        compliance=compliance,
        roadmap=roadmap,
        benchmark_as_of=bench.as_of,
        offline=offline,
    )


def _fmt_money(x: float) -> str:
    if x == float("inf"):
        return "inf"
    return "{:,.2f}".format(x)


def render_report(report: OptReport) -> str:
    """Render an OptReport into the skill's markdown report format."""
    r = report
    m = r.metrics
    sc = r.scorecard
    lines: list[str] = []
    a = lines.append
    a("# Ad Campaign Optimization Report - {} ({})".format(r.brief.platform, r.brief.vertical))
    a("")
    a("## 1. Objective & KPI")
    a("- Objective: {}".format(r.audience.objective))
    a("- Primary KPI: {}".format(r.audience.primary_kpi))
    a("- Segments: {}".format(", ".join(r.audience.segments)))
    a("- LTV: {} | AOV: {}".format(r.audience.ltv, r.audience.aov))
    a("- Audience overlap: {:.0f}%".format(r.audience.overlap_pct))
    if r.audience.notes:
        a("- Notes: {}".format(r.audience.notes))
    a("")
    a("## 2. Efficiency Scorecard (ROAS/CPA vs LTV, CTR/CVR vs benchmark, frequency)")
    a("- Total score: {:.1f}/100 (band {})".format(sc.total, sc.band))
    a("- Economics verdict: {}".format(sc.economics_verdict))
    if sc.ltv_cac_ratio is not None:
        a("- LTV:CAC ratio: {:.1f}:1".format(sc.ltv_cac_ratio))
    a("- Fatigue flag: {}".format("yes" if sc.fatigue else "no"))
    a("")
    a("| Dimension | Weight | Score | Rationale |")
    a("|---|---|---|---|")
    for d in sc.dimensions:
        a("| {} | {:.0%} | {:.0f}/100 | {} |".format(d.name, d.weight, d.score, d.rationale))
    a("")
    a("Raw metrics: spend {} | impr {:,.0f} | clicks {:,.0f} | conv {:,.0f} | "
      "CTR {:.2%} | CVR {:.2%} | CPA {} | ROAS {:.2f} | freq {:.1f}".format(
          _fmt_money(m.spend), m.impressions, m.clicks, m.conversions,
          m.ctr, m.cvr, _fmt_money(m.cpa), m.roas, m.frequency))
    a("")
    a("## 3. Funnel Diagnosis (where it leaks)")
    a("- Leak point: **{}**".format(r.funnel.leak_point))
    a("- Evidence: {}".format(r.funnel.evidence))
    a("- CTR vs benchmark: {:.0%} | CVR vs benchmark: {:.0%}".format(
        r.funnel.ctr_vs_benchmark, r.funnel.cvr_vs_benchmark))
    if r.funnel.notes:
        for n in r.funnel.notes:
            a("- {}".format(n))
    if m.is_ab_test and sc.significance is not None:
        a("")
        a("### A/B significance gate")
        a("- {}".format(sc.significance.verdict))
        a("- p={:.4f} | z={:+.2f} | confidence {:.1%} | required ~{} conversions".format(
            sc.significance.p_value, sc.significance.z,
            sc.significance.confidence, sc.significance.required_conversions))
    a("")
    a("## 4. Compliance Check (policy, claims, targeting limits)")
    a("- Verdict: **{}**{}".format(r.compliance.verdict, " (BLOCKING)" if r.compliance.blocking else ""))
    if r.compliance.findings:
        for f in r.compliance.findings:
            a("  - [{}] {}: {} -> {}".format(f.severity, f.category, f.detail, f.required_fix))
    else:
        a("- No findings.")
    a("")
    a("## 5. Optimization Roadmap (action, expected effect, effort, impact)")
    a("| # | Title | Lever | Expected effect | Effort | Impact |")
    a("|---|---|---|---|---|---|")
    for act in r.roadmap.actions:
        a("| {} | {} | {} | {} | {} | {} |".format(
            act.priority, act.title, act.lever, act.expected_effect, act.effort, act.impact))
    a("")
    a("## 6. Measurement Plan (incrementality/holdout)")
    a(r.roadmap.measurement_plan)
    a("")
    a("## 7. Sources & Currency (dated; offline flag)")
    a("- Benchmark anchor: {} (per-vertical)".format(r.benchmark_as_of))
    a("- Offline / degraded: {}".format("yes - using bundled brain; refresh via tools/knowledge_updater.py" if r.offline else "no"))
    a("- Currency note: benchmarks dated; re-run knowledge_updater.py weekly.")
    a("")
    return "\n".join(lines)
