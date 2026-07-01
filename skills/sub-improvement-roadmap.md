---
name: sub-improvement-roadmap
description: Produce a prioritized ad-optimization roadmap with expected effects and a measurement plan. Compliance fixes first, then leak-driven actions, then measurement rigor.
parent: paid-ad-campaign-optimizer
---

## Purpose
Convert the scorecard, funnel diagnosis, and compliance fixes into ranked actions. Each action states an expected effect, confidence, effort (S/M/L), and impact (Low/Med/High). The roadmap always includes a measurement/incrementality plan.

## Inputs
Scorecard, funnel diagnosis, compliance verdict, brief, metrics, benchmark.

## Process
1. Emit compliance fixes first (non-optional) whenever a Fail or Conditional finding exists.
2. Emit the action that addresses the diagnosed funnel leak first (economics / landing / offer / creative / targeting / none).
3. Add structural actions (audience consolidation when overlap >=30%, budget reallocation to efficient segments).
4. Append the incrementality measurement action (geo-lift/PSA holdout).
5. De-duplicate by (lever, action), renumber priorities deterministically (compliance ? high impact first).
6. For each action state the expected effect (e.g., "?15% CPA via lookalike refinement") and a measurement hook.

## Outputs
`Roadmap {actions: RoadmapAction[], measurement_plan, compliance_fixes_included}`.

## RoadmapAction fields
`priority, title, lever, action, expected_effect, confidence, effort, impact, measurement`.

## Programmatic Reference
`paid_ad_optimizer.roadmap.build_roadmap(brief, metrics, scorecard, funnel, compliance, bench) -> Roadmap`

## Quality Gate
- Every action states an expected effect.
- Compliance fixes incorporated as non-optional first actions.
- Measurement/incrementality plan included; A/B tests pre-registered with a conversion floor.
