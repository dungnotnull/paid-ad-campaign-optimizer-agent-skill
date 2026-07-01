from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
import json

Objective = str  # "awareness" | "consideration" | "conversion"
Platform = str   # "google" | "meta" | "tiktok" | "linkedin" | "microsoft"


@dataclass(frozen=True)
class CampaignBrief:
    platform: Platform
    objective: Objective
    business_goal: str
    vertical: str
    product: str = ""
    audience_description: str = ""
    segments: tuple[str, ...] = ()
    ltv: Optional[float] = None
    aov: Optional[float] = None
    target_cpa: Optional[float] = None
    target_roas: Optional[float] = None
    currency: str = "USD"
    notes: str = ""

    def validate(self) -> None:
        if self.objective not in ("awareness", "consideration", "conversion"):
            raise ValueError("objective must be awareness|consideration|conversion")
        if self.platform not in ("google", "meta", "tiktok", "linkedin", "microsoft", "other"):
            raise ValueError("unsupported platform: " + repr(self.platform))
        if not self.business_goal.strip():
            raise ValueError("business_goal is required")
        if not self.vertical.strip():
            raise ValueError("vertical is required")


@dataclass(frozen=True)
class CampaignMetrics:
    spend: float
    impressions: float
    clicks: float
    conversions: float
    revenue: float = 0.0
    frequency: float = 1.0
    reach: Optional[float] = None
    audience_overlap_pct: float = 0.0
    is_ab_test: bool = False
    ab_control_conversions: float = 0.0
    ab_control_visitors: float = 0.0
    ab_variant_conversions: float = 0.0
    ab_variant_visitors: float = 0.0
    has_incrementality_holdout: bool = False

    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions if self.impressions else 0.0

    @property
    def cvr(self) -> float:
        return self.conversions / self.clicks if self.clicks else 0.0

    @property
    def cpa(self) -> float:
        return self.spend / self.conversions if self.conversions else float("inf")

    @property
    def cpc(self) -> float:
        return self.spend / self.clicks if self.clicks else float("inf")

    @property
    def cpm(self) -> float:
        return self.spend / self.impressions * 1000 if self.impressions else float("inf")

    @property
    def roas(self) -> float:
        return self.revenue / self.spend if self.spend else 0.0

    def validate(self) -> None:
        if self.spend < 0 or self.impressions < 0 or self.clicks < 0:
            raise ValueError("spend/impressions/clicks must be >= 0")
        if self.conversions < 0:
            raise ValueError("conversions must be >= 0")
        if self.frequency < 0:
            raise ValueError("frequency must be >= 0")
        if not (0 <= self.audience_overlap_pct <= 100):
            raise ValueError("audience_overlap_pct must be 0-100")


@dataclass(frozen=True)
class VerticalBenchmark:
    vertical: str
    as_of: str
    ctr_median: float
    cvr_median: float
    cpa_p50: float
    cpa_p75: float
    frequency_fatigue: float
    roas_floor: float
    cpm_median: float = 0.0
    source: str = ""


@dataclass(frozen=True)
class AudienceAnalysis:
    objective: Objective
    primary_kpi: str
    segments: tuple[str, ...]
    ltv: Optional[float]
    aov: Optional[float]
    overlap_pct: float
    notes: str = ""


@dataclass(frozen=True)
class FunnelDiagnosis:
    leak_point: str
    evidence: str
    fatigue: bool
    fatigue_frequency: float
    ctr_vs_benchmark: float
    cvr_vs_benchmark: float
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SignificanceResult:
    is_significant: bool
    confidence: float
    z: float
    p_value: float
    control_rate: float
    variant_rate: float
    lift: float
    required_conversions: int
    verdict: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DimensionScore:
    name: str
    weight: float
    score: float
    rationale: str
    diagnosis: str = ""


@dataclass(frozen=True)
class Scorecard:
    dimensions: tuple[DimensionScore, ...]
    total: float
    band: str
    ltv_cac_ratio: Optional[float]
    economics_verdict: str
    fatigue: bool
    significance: Optional[SignificanceResult]


@dataclass(frozen=True)
class ComplianceFinding:
    category: str
    severity: str
    rule: str
    detail: str
    required_fix: str


@dataclass(frozen=True)
class ComplianceVerdict:
    verdict: str
    findings: tuple[ComplianceFinding, ...]
    blocking: bool

    def to_dict(self) -> dict:
        return {"verdict": self.verdict, "blocking": self.blocking,
                "findings": [asdict(f) for f in self.findings]}


@dataclass(frozen=True)
class RoadmapAction:
    priority: int
    title: str
    lever: str
    action: str
    expected_effect: str
    confidence: str
    effort: str
    impact: str
    measurement: str = ""


@dataclass(frozen=True)
class Roadmap:
    actions: tuple[RoadmapAction, ...]
    measurement_plan: str
    compliance_fixes_included: bool


@dataclass(frozen=True)
class OptReport:
    brief: CampaignBrief
    metrics: CampaignMetrics
    audience: AudienceAnalysis
    funnel: FunnelDiagnosis
    scorecard: Scorecard
    compliance: ComplianceVerdict
    roadmap: Roadmap
    benchmark_as_of: str
    offline: bool

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str, indent=2)
