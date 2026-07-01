# Test Scenarios - Paid Ad Campaign Optimizer (Idea 58)

These six scenarios are the documented acceptance tests for the harness. Each
is implemented as a pytest case in `tests/test_scenarios.py` (named
`test_scenario_N_*`) so the behavior is verified automatically, not just
described. Run with `pytest -q`.

## Scenario 1 - Dropping ROAS diagnosis
- **Input:** Meta campaign, ROAS fell from 3.0 to 1.4 over 4 weeks (frequency up, CTR down).
- **Expected:** funnel diagnosis flags economics + fatigue; economics check vs LTV; creative-refresh + economics roadmap.
- **Pass:** leak point = `economics`; fatigue True; actions state expected effects.
- **Test:** `test_scenario_1_dropping_roas`

## Scenario 2 - Vanity-CTR trap
- **Input:** high CTR (2%) but poor CVR (0.3%) and high CPA (333) vs LTV/3 (133).
- **Expected:** skill judges on CPA/ROAS, flags landing/offer mismatch, never celebrates CTR.
- **Pass:** leak in {economics, landing}; economics verdict `unsustainable`.
- **Test:** `test_scenario_2_vanity_ctr_trap`

## Scenario 3 - Creative fatigue
- **Input:** frequency 8.0, CTR declining.
- **Expected:** fatigue flag, creative refresh + audience expansion.
- **Pass:** fatigue True on both funnel and scorecard; roadmap has a refresh action.
- **Test:** `test_scenario_3_creative_fatigue`

## Scenario 4 - Non-significant A/B test
- **Input:** A/B with 40 total conversions claiming a 5% winner (18 vs 22 over 2000 visitors/arm).
- **Expected:** skill flags insufficient significance; no winner declared.
- **Pass:** `significance.is_significant` is False; verdict mentions insufficient/not significant.
- **Test:** `test_scenario_4_non_significant_ab`

## Scenario 5 - Prohibited health claim (compliance)
- **Input:** supplement ad claiming "cures diabetes", "guaranteed results in 7 days".
- **Expected:** compliance Fail; claim must be removed/substantiated before roadmap.
- **Pass:** verdict `Fail` and blocking; first roadmap action lever = `compliance`.
- **Test:** `test_scenario_5_prohibited_health_claim`

## Scenario 6 - Offline / degraded mode
- **Input:** any campaign with the knowledge brain missing/stale (WebSearch unavailable analog).
- **Expected:** uses bundled brain + flags benchmark-currency limitation.
- **Pass:** `report.offline` is True; rendered report mentions "offline" and "knowledge_updater".
- **Test:** `test_scenario_6_offline_degraded`
