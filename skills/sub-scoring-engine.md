---
name: sub-scoring-engine
description: Score campaign efficiency on economics, targeting, creative, structure, and measurement; diagnose funnel leaks; enforce A/B significance.
parent: paid-ad-campaign-optimizer
---

## Purpose
Produce an economics-grounded efficiency scorecard and pinpoint where the funnel leaks. The scorecard is always relative: each metric is compared to a dated per-vertical benchmark and to LTV-based thresholds, never to absolute vanity numbers.

## Inputs
Campaign metrics (spend, impressions, clicks, conversions, revenue, frequency, overlap), the dated vertical benchmark, LTV/target_roas, and (optional) A/B arm fields.

## Dimensions & Weights
| Dimension | Weight | Anchor |
|---|---|---|
| Economic efficiency | 30% | ROAS/CPA vs LTV & target |
| Targeting quality | 20% | overlap, relevance |
| Creative effectiveness | 20% | AIDA via CTR/CVR vs benchmark; fatigue penalty |
| Structure & budget allocation | 15% | CPM/frequency |
| Measurement rigor | 15% | attribution/incrementality + A/B discipline |

## Process
1. Compare each metric to the dated vertical benchmark and to LTV-based thresholds.
2. Diagnose the funnel by hierarchy: economics > landing/offer (low CVR) > creative/targeting (low CTR). Economics wins because an unprofitable funnel is unfixable by media tactics alone.
3. Detect creative fatigue (frequency ? vertical fatigue threshold). Apply a fatigue penalty to the creative dimension.
4. Run the A/B significance gate; require ~100 conversions/arm and p<0.05 before crediting any winner.
5. Compute the weighted total and map to a letter band (A/B/C/D/F).

## Outputs
`Scorecard {dimensions, total, band, ltv_cac_ratio, economics_verdict, fatigue, significance}` + `FunnelDiagnosis`.

## Programmatic Reference
`paid_ad_optimizer.scoring.score_campaign(brief, metrics, bench, funnel) -> Scorecard`
`paid_ad_optimizer.funnel.diagnose_funnel(brief, metrics, bench) -> FunnelDiagnosis`
`paid_ad_optimizer.significance.ab_significance(metrics) -> SignificanceResult`

## Quality Gate
- Each metric compared to a dated benchmark + economics.
- Funnel leak point identified.
- A/B winner requires significance AND sufficient volume.
