"""Per-vertical benchmark tables for paid-ad performance.

Benchmarks are dated (BENCHMARK_AS_OF). When the knowledge updater refreshes
SECOND-KNOWLEDGE-BRAIN.md with newer dated figures, update this table to keep
the engine current. All ratios computed by the engine are relative to these
anchors, so the engine never judges on absolute vanity numbers in isolation.
"""
from __future__ import annotations
from .models import VerticalBenchmark

# Anchor date for the bundled benchmark set. Refresh via knowledge_updater.py
# findings; keep the as_of per vertical when you revise numbers.
BENCHMARK_AS_OF = "2026-Q2"

_B = VerticalBenchmark

BENCHMARKS: dict[str, VerticalBenchmark] = {
    "ecommerce": _B(
        "ecommerce", BENCHMARK_AS_OF,
        ctr_median=0.0115, cvr_median=0.0270, cpa_p50=20.0, cpa_p75=45.0,
        frequency_fatigue=4.5, roas_floor=2.0, cpm_median=9.5,
        source="Google/Meta paid-shopping aggregated benchmarks 2026-Q2",
    ),
    "saas": _B(
        "saas", BENCHMARK_AS_OF,
        ctr_median=0.0060, cvr_median=0.0120, cpa_p50=120.0, cpa_p75=350.0,
        frequency_fatigue=5.0, roas_floor=1.5, cpm_median=14.0,
        source="B2B SaaS lead-gen benchmarks 2026-Q2",
    ),
    "lead-gen": _B(
        "lead-gen", BENCHMARK_AS_OF,
        ctr_median=0.0080, cvr_median=0.0180, cpa_p50=35.0, cpa_p75=90.0,
        frequency_fatigue=5.0, roas_floor=1.6, cpm_median=11.0,
        source="Lead-gen vertical benchmarks 2026-Q2",
    ),
    "finance": _B(
        "finance", BENCHMARK_AS_OF,
        ctr_median=0.0050, cvr_median=0.0095, cpa_p50=60.0, cpa_p75=180.0,
        frequency_fatigue=5.5, roas_floor=1.8, cpm_median=16.0,
        source="Finance/insurance benchmarks 2026-Q2",
    ),
    "health": _B(
        "health", BENCHMARK_AS_OF,
        ctr_median=0.0070, cvr_median=0.0140, cpa_p50=45.0, cpa_p75=110.0,
        frequency_fatigue=5.0, roas_floor=1.8, cpm_median=13.0,
        source="Health/wellness benchmarks 2026-Q2 (regulated)",
    ),
    "education": _B(
        "education", BENCHMARK_AS_OF,
        ctr_median=0.0075, cvr_median=0.0160, cpa_p50=40.0, cpa_p75=95.0,
        frequency_fatigue=5.0, roas_floor=1.7, cpm_median=12.0,
        source="Education/edtech benchmarks 2026-Q2",
    ),
    "app-install": _B(
        "app-install", BENCHMARK_AS_OF,
        ctr_median=0.0120, cvr_median=0.0200, cpa_p50=3.0, cpa_p75=8.0,
        frequency_fatigue=4.0, roas_floor=1.4, cpm_median=7.0,
        source="App-install CPI benchmarks 2026-Q2",
    ),
    "travel": _B(
        "travel", BENCHMARK_AS_OF,
        ctr_median=0.0090, cvr_median=0.0150, cpa_p50=30.0, cpa_p75=70.0,
        frequency_fatigue=4.5, roas_floor=2.2, cpm_median=10.5,
        source="Travel/hospitality benchmarks 2026-Q2",
    ),
    "retail": _B(
        "retail", BENCHMARK_AS_OF,
        ctr_median=0.0110, cvr_median=0.0250, cpa_p50=18.0, cpa_p75=40.0,
        frequency_fatigue=4.5, roas_floor=2.0, cpm_median=9.0,
        source="Retail foot-traffic/omnichannel benchmarks 2026-Q2",
    ),
    "other": _B(
        "other", BENCHMARK_AS_OF,
        ctr_median=0.0090, cvr_median=0.0200, cpa_p50=30.0, cpa_p75=80.0,
        frequency_fatigue=5.0, roas_floor=1.8, cpm_median=11.0,
        source="Cross-vertical median fallback 2026-Q2",
    ),
}


def get_benchmark(vertical: str) -> VerticalBenchmark:
    """Return the benchmark for a vertical, falling back to the cross-vertical median."""
    key = (vertical or "").strip().lower()
    return BENCHMARKS.get(key) or BENCHMARKS["other"]


def benchmark_currency() -> str:
    """Report the dated currency anchor of the bundled benchmark set."""
    return BENCHMARK_AS_OF
