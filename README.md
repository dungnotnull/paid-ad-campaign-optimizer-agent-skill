# Paid Ad Campaign Optimizer

Audit a Google / Meta / TikTok ad campaign's economics, targeting, and creative against named marketing-measurement frameworks (ROAS/CPA unit economics, attribution & incrementality, AIDA creative, statistical A/B significance), run an ad-policy compliance gate, and emit a prioritized optimization roadmap grounded in unit economics rather than vanity metrics.

This repo ships **two interchangeable execution surfaces that share the same quality gates**:

1. **A deterministic Python engine** (`paid_ad_optimizer`) ? testable, CI-friendly, pure stdlib (no runtime dependencies).
2. **An agent skill** (`skills/*.md`) ? prompt-driven, used when interactive web research and reasoning are required.

Both produce the same 7-section report and enforce the same gates.

## Install

```bash
pip install -e .                       # engine only, zero runtime deps
pip install -e ".[dev]"               # + pytest
pip install -e ".[crawl]"             # + httpx for the weekly knowledge updater
```

## Quick start

```python
from paid_ad_optimizer import CampaignBrief, CampaignMetrics, optimize, render_report

brief = CampaignBrief(
    platform="meta", objective="conversion", business_goal="Grow DTC sales",
    vertical="ecommerce", segments=("purchasers", "lookalike"),
    ltv=120, target_roas=2.5,
)
metrics = CampaignMetrics(
    spend=5000, impressions=400_000, clicks=5200, conversions=110,
    revenue=7200, frequency=8.0, audience_overlap_pct=42,
)
report = optimize(brief, metrics,
                   creative_text="Best supplement - results in 7 days",
                   targeting_terms=("purchasers",))
print(render_report(report))
print(report.to_json())   # machine-readable
```

### CLI knowledge updater

Refresh `SECOND-KNOWLEDGE-BRAIN.md` weekly from ad-platform + measurement sources:

```bash
python tools/knowledge_updater.py --dry-run     # inspect capability, no network
python tools/knowledge_updater.py               # fetch + append (needs httpx)
```

## Architecture

```
paid_ad_optimizer/
  models.py        # dataclasses: brief, metrics, scorecard, verdict, roadmap, report
  benchmarks.py    # dated per-vertical benchmark tables (ecommerce, saas, finance, ...)
  audience.py      # objective -> KPI mapping + overlap gate
  funnel.py        # leak-point diagnosis (economics > landing > creative)
  significance.py  # two-proportion z-test + required-sample-size
  scoring.py       # 5-dimension weighted scorecard + economics verdict
  compliance.py    # ad-policy + claim substantiation gate
  roadmap.py       # prioritized roadmap + measurement plan
  knowledge.py     # SECOND-KNOWLEDGE-BRAIN.md reader/currency check
  pipeline.py      # optimize() + render_report()
skills/            # agent skill files (main + 4 sub-skills)
tools/knowledge_updater.py
tests/             # pytest suite + scenario doc
```

## Quality gates

- Objective + primary KPI set (audience gate).
- Efficiency judged on **economics** (CPA vs LTV / ROAS vs target), not vanity CTR.
- Every metric compared to a **dated** per-vertical benchmark + economics.
- Funnel leak point identified.
- A/B winners require **statistical significance AND sufficient volume** (~100 conversions/arm, p<0.05).
- Compliance gate passes; no Fail item is allowed into the roadmap unresolved.
- Every roadmap action states an **expected effect**; a measurement/incrementality plan is included.
- Benchmarks dated; offline/degraded mode flagged in the report.

## Frameworks (SECOND-KNOWLEDGE-BRAIN.md)

Unit economics (LTV:CAC ? 3:1) ? Funnel diagnosis (Impressions ? CTR ? CVR ? AOV) ? Attribution & incrementality (geo-lift / holdout) ? AIDA creative model ? A/B significance (two-proportion z-test, pre-registration, no peeking) ? Creative fatigue (frequency ?, CTR ?).

## Testing

```bash
pip install -e ".[dev]"
pytest                 # unit + scenario tests
```

## License

MIT. See [LICENSE](LICENSE).
