---
name: sub-compliance-check
description: Ad-policy and claim-substantiation gate that runs before optimization recommendations are emitted. Prohibited/curative claims and sensitive-attribute targeting block the roadmap.
parent: paid-ad-campaign-optimizer
---

## Purpose
Prevent recommendations that violate platform ad policy or advertising law. This gate is mandatory and runs before the roadmap; any Fail-severity finding blocks the roadmap until the fix is incorporated as a non-optional first action.

## Inputs
Creative/ad copy text, claims, vertical, targeting terms/attributes, landing-page consistency signals.

## Rules (deterministic, rule-based)
1. **Prohibited/curative claims:** "cures diabetes", "cures cancer", "cure", "guaranteed cure", "100% guaranteed", "miracle", "risk-free/no risk", "get rich", "lose weight fast" ? Fail; remove or substantiate.
2. **Superlatives needing proof:** best, #1/number one, guaranteed, proven, approved, certified, fastest/cheapest, "results in N days/weeks" ? Conditional; attach proof or soften.
3. **Special-category targeting limits:** housing, employment, credit, finance, health, political, crypto ? Info; demographic targeting restricted; financial-outcome and curative language in regulated verticals escalate.
4. **Sensitive attributes:** race, ethnicity, religion, sexual orientation, disability, financial hardship ? Fail if targeted.
5. **Landing-page consistency:** if the creative references a specific offer/price not echoed in the landing goal ? Conditional.

## Outputs
`ComplianceVerdict {verdict: Pass|Conditional|Fail, findings, blocking}`. `blocking=True` when any finding is Fail.

## Programmatic Reference
`paid_ad_optimizer.compliance.check_compliance(brief, metrics, creative_text, targeting_terms) -> ComplianceVerdict`

## Quality Gate
- Policy + claim substantiation explicitly verified.
- No Fail item passes unresolved into the roadmap (compliance fixes are non-optional first actions).
- A rule-based engine does not replace legal review for regulated verticals; escalate health/finance/credit/political to legal.
