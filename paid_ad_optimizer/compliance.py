"""Compliance check engine: ad-policy + claim substantiation gate.

Implements a deterministic, rule-based pass over the creative text and the
targeting/vertical context. No rule-based engine replaces legal review for
regulated verticals, but this gate catches the common prohibited/unsupported
claims and special-category targeting limits *before* the roadmap emits
recommendations. A Fail severity blocks the roadmap: compliance fixes must be
incorporated as non-optional first actions.
"""
from __future__ import annotations
import re
from .models import CampaignBrief, CampaignMetrics, ComplianceFinding, ComplianceVerdict

# Prohibited/regulated verticals and the policy signal words we test for.
PROHIBITED_CLAIMS = {
    "cure": "claims to cure a disease",
    "guaranteed cure": "guaranteed-cure claim",
    "cures diabetes": "explicit disease-cure claim (health)",
    "100% guaranteed": "absolute-guarantee claim",
    "miracle": "miracle-result claim",
    "risk-free": "risk-free investment claim",
    "no risk": "no-risk investment claim",
    "get rich": "get-rich-quick claim",
    "lose weight fast": "unsubstantiated weight-loss claim",
    "cures cancer": "explicit disease-cure claim (health)",
}

# Superlatives that require substantiation evidence (not outright prohibited).
SUPERLATIVE_PATTERN = re.compile(
    r"\b(best|number one|#1|guaranteed|proven|approved|certified|fastest|cheapest|"
    r"results in \d+ days|results in \d+ weeks)\b",
    re.IGNORECASE,
)

# Special categories that restrict targeting on Google/Meta/TikTok.
SPECIAL_CATEGORIES = {"housing", "employment", "credit", "finance", "health",
                      "political", "crypto"}

# Sensitive personal attributes that cannot be targeted.
SENSITIVE_TARGETING_TERMS = ("race", "ethnicity", "religion", "sexual orientation",
                             "disability", "financial hardship")


def check_compliance(brief: CampaignBrief, metrics: CampaignMetrics,
                     creative_text: str = "",
                     targeting_terms: tuple[str, ...] = ()) -> ComplianceVerdict:
    """Run the deterministic compliance gate.

    Args:
      brief: campaign brief (vertical drives special-category rules).
      metrics: campaign metrics (currently informational; reserved for landing
        page consistency checks in future revisions).
      creative_text: the ad copy / claims to vet.
      targeting_terms: targeting keywords/attributes being used.
    """
    text = (creative_text or "").strip()
    vertical = (brief.vertical or "").strip().lower()
    findings: list[ComplianceFinding] = []
    lower = text.lower()

    # 1) Prohibited/unsupported claims.
    for phrase, rule in PROHIBITED_CLAIMS.items():
        if phrase in lower:
            findings.append(ComplianceFinding(
                category="claim", severity="fail", rule=rule,
                detail="Creative contains: '{}'.".format(phrase),
                required_fix="Remove or substantiate with verifiable evidence; "
                             "disease/curative claims require regulatory compliance review.",
            ))

    # 2) Superlatives needing proof.
    for m in SUPERLATIVE_PATTERN.finditer(text):
        findings.append(ComplianceFinding(
            category="claim", severity="conditional", rule="superlative-needs-proof",
            detail="Superlative/absolute term '{}' requires substantiation.".format(m.group(0)),
            required_fix="Attach proof (study, certification, comparison) or soften the claim.",
        ))

    # 3) Special-category targeting limits.
    if vertical in SPECIAL_CATEGORIES:
        findings.append(ComplianceFinding(
            category="targeting", severity="info",
            rule="special-category-targeting-limit",
            detail="Vertical '{}' is a special/advertising-sensitive category; "
                   "demographic and certain interest targeting is restricted.".format(vertical),
            required_fix="Use only compliant targeting; document regulatory disclosures.",
        ))
        if vertical == "finance" and re.search(r"\b(investment|returns|profit)\b", lower):
            findings.append(ComplianceFinding(
                category="claim", severity="conditional", rule="financial-claim-disclosure",
                detail="Financial-outcome language present in a regulated vertical.",
                required_fix="Add required risk disclosures and licensing info; legal review.",
            ))
        if vertical == "health" and re.search(r"\b(cure|treat|heal|disease)\b", lower):
            findings.append(ComplianceFinding(
                category="claim", severity="fail", rule="health-curative-claim",
                detail="Curative/treatment language in health vertical.",
                required_fix="Remove curative claims; restrict to structure/function wording with disclaimer.",
            ))

    # 4) Sensitive personal attributes cannot be targeted.
    terms_lower = [t.lower() for t in targeting_terms]
    for term in SENSITIVE_TARGETING_TERMS:
        if any(term in t for t in terms_lower):
            findings.append(ComplianceFinding(
                category="targeting", severity="fail",
                rule="sensitive-attribute-targeting",
                detail="Targeting references sensitive attribute '{}'.".format(term),
                required_fix="Remove sensitive-attribute targeting; switch to behavior/context signals.",
            ))

    # 5) Landing-page consistency: if creative references a specific offer/price,
    # require the brief.business_goal to mention it (proxy for landing alignment).
    if re.search(r"\b\d+% off|\$\d+|free (trial|shipping)\b", lower):
        if not (brief.business_goal and re.search(r"\b\d+%|\$\d+|free", brief.business_goal.lower())):
            findings.append(ComplianceFinding(
                category="landing", severity="conditional",
                rule="landing-offer-consistency",
                detail="Creative references a specific offer/price not echoed in the stated goal/landing.",
                required_fix="Align the landing page offer with the creative promise.",
            ))

    has_fail = any(f.severity == "fail" for f in findings)
    has_cond = any(f.severity == "conditional" for f in findings)
    if has_fail:
        verdict = "Fail"
    elif has_cond:
        verdict = "Conditional"
    else:
        verdict = "Pass"

    return ComplianceVerdict(
        verdict=verdict,
        findings=tuple(findings),
        blocking=has_fail,
    )
