# PROJECT-detail.md — Paid Ad Campaign Optimizer (Idea 58)

## Executive Summary
A harness that audits a paid campaign's economics, targeting, and creative against named measurement frameworks, checks ad-policy compliance, and emits a prioritized optimization roadmap.

## Problem Statement
Advertisers optimize to vanity metrics, misattribute conversions, and run creative that fatigues. This skill grounds optimization in unit economics and measurement science.

## Target Users & Use Cases
- **SMB advertiser:** "Why is my ROAS dropping?" → diagnosis + fixes.
- **Performance marketer:** "Audit my Meta account structure" → structure + targeting review.
- **Founder:** "Is my CAC sustainable?" → CPA vs LTV economics check.

## Harness Architecture
```
/paid-ad-campaign-optimizer
  → sub-audience-analysis   (objective, funnel, audience)   [gate: objective + KPI set]
  → [main] research         (platform/measurement norms)    [gate: benchmarks dated]
  → sub-scoring-engine      (efficiency score)              [gate: metrics vs benchmark + economics]
  → sub-compliance-check    (ad policy + claims)            [gate: policy verified]
  → sub-improvement-roadmap (budget/targeting/creative)     [gate: each action with expected effect]
  → [main] synthesize
```

## Full Sub-Skill Catalog
| Sub-skill | Purpose | Inputs | Outputs | Tools | Gate |
|-----------|---------|--------|---------|-------|------|
| sub-audience-analysis | Objective & audience | brief, platform | audience+KPI | Read, WebSearch | Objective + KPI set |
| sub-scoring-engine | Efficiency score | metrics | score + diagnosis | Read | Metrics vs benchmark + economics |
| sub-compliance-check | Ad policy | creative, claims | policy verdict | Read, WebSearch | Policy + claims verified |
| sub-improvement-roadmap | Optimization plan | scores | roadmap | Write | Each action expected effect |

## Skill File Format Specification
Per Claude skill standard; see skills/main.md.

## E2E Execution Flow
1. Audience analysis sets objective (awareness/consideration/conversion) and primary KPI. 2. Research confirms current platform bidding/measurement norms (e.g., post-iOS attribution, value-based bidding). 3. Scoring evaluates ROAS/CPA vs LTV, CTR/CVR vs vertical benchmark, frequency/fatigue, account structure, audience overlap. 4. Compliance checks ad policy (prohibited categories, claim substantiation, special-category targeting limits). 5. Roadmap proposes budget reallocation, targeting refinement, creative refresh, and a measurement plan (incrementality/holdout). 6. Render.
Error handling: insufficient conversion volume for significance → flag; regulated vertical → stricter compliance; offline → use brain + flag.

## SECOND-KNOWLEDGE-BRAIN Integration
Sources: platform ad docs, MSI, ARF/IAB, SSRN marketing. Weekly append.

## Supporting Tools Spec
`knowledge_updater.py`: queries on ad platform & measurement changes; weekly cron; dedupe by hash.

## Quality Gates
- Efficiency judged on economics (CPA vs LTV / ROAS), not vanity metrics.
- A/B claims require statistical significance / sufficient volume.
- Compliance check passed (policy + claim substantiation).
- Roadmap actions state expected effect; benchmarks dated; offline flagged.

## Test Scenarios (summary)
1. Dropping ROAS diagnosis. 2. Vanity-CTR trap. 3. Creative fatigue (high frequency). 4. Non-significant A/B test. 5. Prohibited health claim (compliance). (Full set in tests/.)

## Key Design Decisions
1. Economics over vanity metrics. 2. Significance required for test conclusions. 3. Compliance gate mandatory. 4. Measurement plan (incrementality) recommended. 5. Benchmarks dated per vertical.
