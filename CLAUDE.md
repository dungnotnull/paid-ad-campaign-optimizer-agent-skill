# CLAUDE.md - Paid Ad Campaign Optimizer Skill (Idea 58)

**Skill name:** `paid-ad-campaign-optimizer`
**Tagline:** Budget/targeting/creative optimization for Google/Meta/TikTok Ads against measurement frameworks.
**Current phase:** Production-complete (Phases 0-5). All deliverables implemented as real, tested code; ready for open source.
**Source idea:** 58 - Analyze & optimize paid ad campaigns (Google/Facebook/TikTok Ads), evaluating budget efficiency, targeting and creative, grounded in world-renowned marketing-measurement methods, with improvement recommendations; continuously crawl papers/docs to stay current.
**Cluster:** `marketing-content-branding`

## Problem This Skill Solves
Advertisers waste budget on poorly measured campaigns. This skill audits a campaign's structure, targeting, creative, and metrics against named frameworks (ROAS/CPA economics, incrementality/attribution, AIDA creative, statistical A/B significance), scores efficiency, runs an ad-policy compliance check, and emits an optimization roadmap.

## Two Execution Surfaces (same quality gates)
1. **Deterministic Python engine** (`paid_ad_optimizer/`): pure stdlib, testable, CI-friendly. `from paid_ad_optimizer import optimize, render_report`.
2. **Agent skill** (`skills/*.md`): prompt-driven, for interactive web research + reasoning.

Both produce the same 7-section report and enforce the same gates.

## Harness Flow Summary
1. **Audience analysis** (`sub-audience-analysis`) - objective, funnel stage, audience, platform. [gate: objective + KPI set]
2. **Research** (main) - verify current platform/measurement norms vs SECOND-KNOWLEDGE-BRAIN.md. [gate: benchmarks dated]
3. **Scoring** (`sub-scoring-engine`) - 5-dim weighted scorecard (ROAS, CPA, CTR, CVR, frequency) + funnel diagnosis.
4. **Compliance** (`sub-compliance-check`) - ad policy + claim substantiation. [gate: no Fail unresolved]
5. **Roadmap** (`sub-improvement-roadmap`) - budget/targeting/creative actions, each with expected effect + measurement plan.

## Sub-skills
`sub-audience-analysis.md` - `sub-scoring-engine.md` - `sub-compliance-check.md` - `sub-improvement-roadmap.md`

## Tools Required
WebSearch, WebFetch, Read, Write, Bash.

## Knowledge Sources
Google/Meta/TikTok Ads docs, Marketing Science Institute, ARF/IAB measurement standards, SSRN marketing, industry benchmark reports.

## Supporting Python Tools
- `tools/knowledge_updater.py` - crawl -> SECOND-KNOWLEDGE-BRAIN.md (dedupe by hash; httpx/crawl4ai backends; dry-run; exit codes).
- `paid_ad_optimizer/` - the engine package (models, benchmarks, audience, funnel, significance, scoring, compliance, roadmap, knowledge, pipeline).

## Testing
`pytest -q` runs 57 unit + scenario tests; all green.

## Active Development Tasks
- [x] Scaffold deliverables.
- [x] Add per-vertical benchmark tables (in `benchmarks.py` + SECOND-KNOWLEDGE-BRAIN.md).
- [x] Production-grade engine implementation.
- [x] Real pytest suite (6 scenarios + unit tests).
- [x] Open-source packaging (pyproject.toml, README, LICENSE).

## Reference Docs
PROJECT-detail.md - PROJECT-DEVELOPMENT-PHASE-TRACKING.md - SECOND-KNOWLEDGE-BRAIN.md - README.md
