"""Statistical significance for A/B conversion-rate tests.

Implements a two-proportion z-test with pooled variance and a normal
approximation, plus a sample-size estimate derived from the minimum detectable
effect. We deliberately avoid peeking: callers should pre-register the required
per-arm conversions and only declare a winner once each arm reaches the volume
floor (~100 conversions/arm) AND the two-tailed p-value is below alpha.

Design note: the z-test itself decides significance. The volume floor
(MIN_CONVERSIONS_PER_ARM) is a separate guard against tiny-sample noise; it does
not override a genuinely significant large-sample result. The
`required_conversions` figure returned is a *planning* number (per-arm
conversions needed to detect a 5% relative MDE at 80% power) for designing the
next test, not a blocking threshold for the current one.
"""
from __future__ import annotations
import math
from statistics import NormalDist
from .models import CampaignMetrics, SignificanceResult

DEFAULT_ALPHA = 0.05
# Pragmatic minimum conversions per arm before any winner can be declared,
# regardless of z-score, to avoid low-volume false positives (industry rule of
# thumb: ~100 conversions/arm for stable conversion-rate estimates).
MIN_CONVERSIONS_PER_ARM = 100


def _norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _two_tailed_p(z: float) -> float:
    return 2.0 * (1.0 - _norm_cdf(abs(z)))


def ab_significance(metrics: CampaignMetrics, alpha: float = DEFAULT_ALPHA,
                    min_conversions_per_arm: int = MIN_CONVERSIONS_PER_ARM) -> SignificanceResult:
    """Run a two-proportion z-test on the A/B arms stored on `metrics`.

    Returns a SignificanceResult. If `metrics.is_ab_test` is False, returns an
    inert non-significant result with a verdict explaining no test was provided.
    """
    if not metrics.is_ab_test:
        return SignificanceResult(
            is_significant=False, confidence=0.0, z=0.0, p_value=1.0,
            control_rate=0.0, variant_rate=0.0, lift=0.0,
            required_conversions=min_conversions_per_arm,
            verdict="No A/B test reported; significance gate not exercised.",
        )

    c_conv = float(metrics.ab_control_conversions)
    c_vis = float(metrics.ab_control_visitors)
    v_conv = float(metrics.ab_variant_conversions)
    v_vis = float(metrics.ab_variant_visitors)

    if c_vis <= 0 or v_vis <= 0:
        return SignificanceResult(
            is_significant=False, confidence=0.0, z=0.0, p_value=1.0,
            control_rate=c_conv / c_vis if c_vis else 0.0,
            variant_rate=v_conv / v_vis if v_vis else 0.0, lift=0.0,
            required_conversions=min_conversions_per_arm,
            verdict="A/B test has zero visitors in an arm; cannot evaluate.",
        )

    p_c = c_conv / c_vis
    p_v = v_conv / v_vis
    pooled = (c_conv + v_conv) / (c_vis + v_vis)
    se = math.sqrt(pooled * (1.0 - pooled) * (1.0 / c_vis + 1.0 / v_vis))
    z = (p_v - p_c) / se if se != 0.0 else 0.0
    p_value = _two_tailed_p(z)
    confidence = 1.0 - p_value

    min_conv_each = min(c_conv, v_conv)
    sufficient_volume = min_conv_each >= min_conversions_per_arm
    is_sig = (p_value < alpha) and sufficient_volume

    # Planning number: per-arm conversions to detect a 5% relative MDE.
    required = required_sample_size(p_c, alpha=alpha, mde=0.05) if p_c > 0 else min_conversions_per_arm

    if not sufficient_volume:
        verdict = (
            "Insufficient volume to declare a winner "
            "(min arm {:.0f} conversions vs {:.0f} required/arm). "
            "Do not act on this result; keep collecting data.".format(
                min_conv_each, float(min_conversions_per_arm))
        )
    elif is_sig:
        verdict = (
            "Significant at alpha={:.2f} (p={:.4f}, z={:+.2f}); variant lift is "
            "{:+.1%} relative. Winner can be rolled out with a holdout to confirm "
            "incrementality.".format(alpha, p_value, z, (p_v - p_c) / p_c if p_c else 0.0)
        )
    else:
        verdict = (
            "Not significant at alpha={:.2f} (p={:.4f}, z={:+.2f}); treat arms as "
            "equivalent or keep testing.".format(alpha, p_value, z)
        )

    return SignificanceResult(
        is_significant=is_sig,
        confidence=float(min(1.0, confidence)),
        z=float(z),
        p_value=float(p_value),
        control_rate=float(p_c),
        variant_rate=float(p_v),
        lift=float((p_v - p_c) / p_c) if p_c else 0.0,
        required_conversions=int(math.ceil(required)),
        verdict=verdict,
    )


def required_sample_size(baseline_rate: float, alpha: float = DEFAULT_ALPHA,
                         mde: float = 0.05, power: float = 0.8) -> int:
    """Per-arm *conversions* needed to detect a relative MDE at the given power.

    Uses the standard difference-in-proportions sample-size formula and converts
    the per-arm visitor count to expected conversions via the baseline rate. This
    is a planning figure for designing the next test, not a blocking threshold for
    the current one (the z-test plus MIN_CONVERSIONS_PER_ARM floor govern that).
    """
    if not 0.0 < baseline_rate < 1.0:
        return MIN_CONVERSIONS_PER_ARM
    delta = baseline_rate * mde
    if delta <= 0:
        return MIN_CONVERSIONS_PER_ARM
    # stdlib inverse normal CDF (Python 3.8+); avoids scipy dependency.
    z_alpha = NormalDist().inv_cdf(1.0 - alpha / 2.0)   # two-tailed
    z_power = NormalDist().inv_cdf(power)
    p1, p2 = baseline_rate, baseline_rate + delta
    p_bar = (p1 + p2) / 2.0
    n_visitors_per_arm = ((z_alpha + z_power) ** 2) * (2.0 * p_bar * (1.0 - p_bar)) / (delta ** 2)
    conversions_per_arm = n_visitors_per_arm * baseline_rate
    return int(math.ceil(max(conversions_per_arm, MIN_CONVERSIONS_PER_ARM)))
