"""Unit tests for the compliance gate."""
from paid_ad_optimizer.compliance import check_compliance
from conftest import make_brief, make_metrics


def test_prohibited_health_claim_fails():
    b = make_brief(vertical="health")
    v = check_compliance(b, make_metrics(),
                         creative_text="Miracle supplement cures diabetes, guaranteed!",
                         targeting_terms=())
    assert v.verdict == "Fail"
    assert v.blocking is True
    assert any(f.rule.startswith("claims to cure") or "cure" in f.rule for f in v.findings)


def test_superlative_is_conditional_not_fail():
    v = check_compliance(make_brief(), make_metrics(),
                         creative_text="The best running shoes, proven fast.",
                         targeting_terms=())
    assert v.verdict == "Conditional"
    assert any(f.severity == "conditional" for f in v.findings)
    assert v.blocking is False


def test_clean_creative_passes():
    v = check_compliance(make_brief(), make_metrics(),
                         creative_text="Comfortable running shoes for daily training.",
                         targeting_terms=("runners",))
    assert v.verdict == "Pass"
    assert v.findings == ()


def test_sensitive_attribute_targeting_fails():
    v = check_compliance(make_brief(), make_metrics(),
                         creative_text="Great product.",
                         targeting_terms=("race", "ethnicity"))
    assert v.verdict == "Fail"
    assert any(f.rule == "sensitive-attribute-targeting" for f in v.findings)


def test_finance_vertical_disclosure_required():
    b = make_brief(vertical="finance")
    v = check_compliance(b, make_metrics(),
                         creative_text="Earn guaranteed investment returns of 10%.",
                         targeting_terms=())
    assert v.verdict in ("Fail", "Conditional")
    assert any(f.category == "claim" for f in v.findings)


def test_landing_inconsistency_conditional():
    v = check_compliance(make_brief(business_goal="brand awareness only"),
                         make_metrics(),
                         creative_text="50% off everything today!",
                         targeting_terms=())
    assert any(f.rule == "landing-offer-consistency" for f in v.findings)
