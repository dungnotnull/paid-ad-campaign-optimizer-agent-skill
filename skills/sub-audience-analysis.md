---
name: sub-audience-analysis
description: Define campaign objective, primary KPI, target audience, and platform before optimization. Maps objective to the correct success KPI and flags audience overlap/cannibalization.
parent: paid-ad-campaign-optimizer
---

## Purpose
Anchor optimization on a single objective and the right success metric. The KPI must match the objective so the rest of the harness never judges a conversion campaign on a vanity CTR or an awareness campaign on CPA.

## Inputs
- Campaign brief: platform, vertical, business_goal, segments, ltv, aov, target_cpa, target_roas.
- Current metrics (for overlap %): audience_overlap_pct, frequency.

## Objective ? KPI mapping
| Objective | Primary KPI | Guardrail KPIs |
|---|---|---|
| awareness | reach | cpm, frequency, recall |
| consideration | ctr | cpc, engagement_rate, video_view_rate |
| conversion | cpa | roas, cvr, ltv_cac |

## Process
1. Set objective (awareness/consideration/conversion) and the matching primary KPI. Reject unknown objectives.
2. Define audience segments and check overlap/cannibalization (>=30% overlap ? consolidate/exclude).
3. Capture LTV/AOV for economics-based judging; if target_cpa > LTV/3, flag unsustainable.
4. **Gate:** block the harness if objective or primary KPI is undefined.

## Outputs
`AudienceAnalysis {objective, primary_kpi, segments, ltv, aov, overlap_pct, notes}`.

## Programmatic Reference
`paid_ad_optimizer.audience.audience_analysis(brief, metrics) -> AudienceAnalysis`
- Raises `ValueError` when the objective is unknown or inputs are invalid (the gate).

## Quality Gate
- Objective and primary KPI explicitly set.
- Overlap >=30% surfaced as an action input to the roadmap.
