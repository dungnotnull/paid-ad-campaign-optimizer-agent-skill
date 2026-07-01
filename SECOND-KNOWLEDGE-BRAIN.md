# SECOND-KNOWLEDGE-BRAIN.md - Paid Ad Campaign Optimizer (Idea 58)

Grown weekly by `tools/knowledge_updater.py`. The engine reads this file via
`paid_ad_optimizer.knowledge.load_brain()` to confirm benchmark currency and
surface recent findings in the report's Sources & Currency section.

## Core Concepts & Frameworks
- **Unit economics:** ROAS = revenue/ad spend; CPA/CAC vs LTV (sustainable when LTV:CAC >= 3, payback < 12mo).
- **Funnel metrics:** Impressions -> CTR -> CVR -> AOV; diagnose where the drop occurs.
- **Attribution & incrementality:** last-click overstates paid; use holdout/geo-lift to measure true incremental effect (post-iOS signal loss).
- **AIDA creative model:** Attention-Interest-Desire-Action for ad creative.
- **A/B significance:** require adequate sample/conversions before declaring a winner (avoid peeking; ~95% confidence, ~100 conversions/arm).
- **Creative fatigue:** rising frequency + falling CTR signals refresh need.

## Scoring Dimensions (this skill)
| Dimension | Weight | Anchor |
|-----------|--------|--------|
| Economic efficiency (ROAS/CPA vs LTV) | 30% | Unit economics |
| Targeting quality (overlap, relevance) | 20% | Audience strategy |
| Creative effectiveness | 20% | AIDA, CTR/CVR |
| Account structure & budget allocation | 15% | Platform best practice |
| Measurement rigor (attribution) | 15% | Incrementality |

## Per-Vertical Benchmark Tables (engine anchors, dated 2026-Q2)

Bundled in `paid_ad_optimizer/benchmarks.py` and used by the scoring/funnel
engines. Each metric is judged *relative* to its vertical anchor and to LTV-based
economics, never in absolute isolation. Refresh these via `knowledge_updater.py`
findings; bump the `as_of` when numbers are revised.

| Vertical | CTR median | CVR median | CPA p50 | CPA good ceiling (p75) | Frequency fatigue | ROAS floor | CPM median |
|---|---|---|---|---|---|---|---|
| ecommerce | 1.15% | 2.70% | 20.00 | 45.00 | 4.5 | 2.0 | 9.50 |
| saas | 0.60% | 1.20% | 120.00 | 350.00 | 5.0 | 1.5 | 14.00 |
| lead-gen | 0.80% | 1.80% | 35.00 | 90.00 | 5.0 | 1.6 | 11.00 |
| finance | 0.50% | 0.95% | 60.00 | 180.00 | 5.5 | 1.8 | 16.00 |
| health | 0.70% | 1.40% | 45.00 | 110.00 | 5.0 | 1.8 | 13.00 |
| education | 0.75% | 1.60% | 40.00 | 95.00 | 5.0 | 1.7 | 12.00 |
| app-install | 1.20% | 2.00% | 3.00 | 8.00 | 4.0 | 1.4 | 7.00 |
| travel | 0.90% | 1.50% | 30.00 | 70.00 | 4.5 | 2.2 | 10.50 |
| retail | 1.10% | 2.50% | 18.00 | 40.00 | 4.5 | 2.0 | 9.00 |
| other (fallback) | 0.90% | 2.00% | 30.00 | 80.00 | 5.0 | 1.8 | 11.00 |

Source: Google/Meta/TikTok paid-search and paid-social aggregated benchmarks,
Marketing Science Institute, ARF/IAB measurement standards (2026-Q2). Treat as
directional anchors, not absolute targets; always combine with first-party
LTV-based economics.

## Key Research / Sources
| Title | Source | Year | Link | Relevance |
|-------|--------|------|------|-----------|
| Incrementality measurement | MSI | 2023 | msi.org | True effect |
| Digital ad effectiveness | SSRN | 2022 | ssrn.com | Attribution bias |
| Privacy-safe measurement (SKAN/consent) | Platform docs | 2024 | support.google.com / business.tiktok.com | Attribution signal loss |

## Authoritative Data Sources
Google/Meta/TikTok Ads help centers, Marketing Science Institute, ARF/IAB, SSRN marketing, dated industry benchmark reports.

## Analytical Frameworks
Unit economics (LTV:CAC) - Funnel diagnosis - Attribution/incrementality - AIDA - A/B significance.

## Self-Update Protocol
- Queries: "ad platform update", "attribution measurement", "ad benchmark CTR CVR", "privacy ad targeting".
- Sources: platform docs, MSI, IAB, ARF. Frequency: weekly (cron).
- Append: `- [DATE] Title - Source - URL <!--h:hash-->`. Dedupe by hash (`paid_ad_optimizer.knowledge`).

## Knowledge Update Log
- [2026-06-18] Seed entry - frameworks documented - internal
- [2026-06-18] Per-vertical benchmark tables added - internal
