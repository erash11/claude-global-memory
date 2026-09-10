# CMJ measurement properties in D1 football: what these metrics can and cannot see

**Status:** analysis complete
**Data:** 185 athletes, 92,550 athlete-metric-days, 5,930 retest pairs per metric, 2023–2025
**Reproduce:** `python -m src.research.measurement`

## Why this comes first

Ward's framing puts measurement ahead of modelling — validity, reliability,
responsiveness — because a metric that cannot resolve a meaningful change will
return a null regardless of how well the study is designed.

We arrived here the hard way. Six separate attempts to detect a practice-load
effect on readiness returned nothing. Before concluding that practice load has
no effect, we checked whether our instruments could have seen one.

## Method

| Quantity | Definition |
|---|---|
| **Typical error (TE)** | SD(difference) / √2 across consecutive **same-weekday** tests ≤10 days apart |
| **SWC** | 0.2 × between-athlete SD (conventional smallest worthwhile change) |
| **SWC / TE** | Below 1, the metric cannot resolve a worthwhile change even in principle |

Same-weekday pairing is deliberate. Monday and Thursday sit at different points
in the training week, so pooling them would charge real weekly rhythm to
measurement noise and overstate TE.

## Results

| Metric | TE % | SWC/TE | Verdict |
|---|---|---|---|
| Concentric Impulse | 2.9 | 0.99 | cannot resolve SWC |
| Peak Power / BM | 3.8 | 0.78 | cannot resolve SWC |
| P1 Concentric Impulse | 4.8 | 0.69 | cannot resolve SWC |
| Jump Height (Imp-Mom) | 5.7 | 0.63 | cannot resolve SWC |
| P2 Concentric Impulse | 6.3 | 0.57 | cannot resolve SWC |
| Concentric Impulse-100ms | 8.4 | 0.50 | cannot resolve SWC |
| **RSI-modified** | **8.8** | **0.48** | cannot resolve SWC |
| Eccentric Duration | 6.6 | 0.42 | cannot resolve SWC |
| Eccentric Deceleration RFD / BM | 18.4 | 0.42 | cannot resolve SWC |
| Eccentric Peak Power / BM | 13.4 | 0.34 | cannot resolve SWC |

**None of the ten metrics resolves the smallest worthwhile change at
individual, week-to-week resolution.**

## Two caveats, both of which make this less damning than it reads

1. **TE here is week-to-week typical variation, not instrument reliability.**
   It includes genuine biological fluctuation over up to 10 days. Same-session
   repeat-trial TE would be considerably smaller. What is reported is the right
   denominator for *weekly monitoring decisions* — which is the use case — but
   it should not be quoted as the reliability of the force plate.

2. **The 0.2 × SD convention is harsh in a homogeneous population.** D1
   football athletes within a position band are similar to each other, so the
   between-athlete SD is small, so the SWC is small. This is a known limitation
   of the convention in elite samples rather than a property of these metrics
   specifically.

Both caveats push in the same direction: the ratios above are pessimistic. The
practical conclusion survives anyway.

## What follows operationally

- **Do not act on a single athlete's single-week change.** In every metric, a
  one-week move is dominated by noise. This is the most important line in this
  document.
- **Trends across several tests are the usable unit**, which is an argument for
  denser, more regular testing rather than less. See
  `camp_2026_testing_ask.md`.
- **Stop defaulting to RSI-modified.** It is the field's habitual readiness
  metric and it carries **more than twice** the week-to-week noise of Peak
  Power / BM (8.8% vs 3.8%) in this population.
- **Peak Power / BM is the best headline metric**, on the reliability /
  responsiveness trade-off rather than on either alone. Concentric Impulse is
  quieter (TE 2.9%, ratio 0.99) but essentially inert — its mean Monday →
  Thursday change is +0.06%, so it is stable precisely because nothing moves
  it. Peak Power / BM is second-quietest and second-most responsive (+0.90%).

## IMTP: same analysis, and the cadence implication

`python -m src.research.measurement --imtp --timescale`

| IMTP metric | TE % | SWC/TE |
|---|---|---|
| Peak Vertical Force | 8.8 | 0.39 |
| Peak Vertical Force / BM | 8.9 | 0.35 |
| RFD − 200ms | 23.8 | 0.23 |
| RFD − 100ms | 36.6 | 0.21 |

**The RFD metrics are not usable at any cadence.** 24–37% week-to-week noise
means a change would have to be enormous before it carried information.

### How fast does each quality actually change?

For every within-athlete pair of tests, the spread of percent change against
the gap between them. Pure noise stays flat as the gap widens; a developing
quality spreads out.

| Gap | IMTP Peak Force / BM | CMJ Peak Power / BM |
|---|---|---|
| 0–10 days | 13.2% | 6.6% |
| 10–25 days | 14.9% | 6.7% |
| 25–50 days | 16.5% | 6.8% |
| 50–100 days | 16.4% | 7.6% |
| 100–200 days | 17.3% | 8.0% |

Because noise and real drift add in quadrature, they separate:

- **IMTP: noise floor 13.2%, real change accumulated over 3–6 months ≈ 11.1%.**
  Half a season of genuine strength change is *smaller than one week of
  measurement noise.*
- **CMJ: noise floor 6.6%** — half the IMTP figure — and it is the measure
  that responds within a week.

### What follows

Maximal strength is a slow-adapting quality and the data agrees with the
physiology. **A weekly IMTP is sampling roughly ten times faster than the
thing it measures changes.** Four well-spaced tests per season (camp start,
camp end, mid-season, season end) preserve every meaningful comparison,
because those are all month-plus intervals.

This matters operationally because IMTP and CMJ compete for the same slot: of
2,029 IMTP athlete-days in 2023–25, exactly **one** also has a CMJ. Monday is
IMTP, Thursday is CMJ, and that is precisely why only 20% of athlete-weeks
have the paired CMJ needed to see what a training week did.

**Boundary of this claim:** it concerns measurement value only. If the IMTP
functions as a training or priming stimulus, that is a separate justification
this analysis does not touch and should not be used to override.

## A methods finding worth publishing separately

While designing the companion heterogeneity analysis we found that the standard
approach to testing whether athletes differ in their response — fit a slope per
athlete, then test the spread of those slopes with Cochran's Q against a
chi-square reference — **rejects the null 90.7% of the time when nothing is
happening**, at the sample sizes normal in this field (8–12 observations per
athlete).

The cause is that per-athlete slope standard errors are estimated from as few
as one residual degree of freedom, which breaks the chi-square approximation.
The null Q 95th percentile by simulation is **1052** against **82.6** by
chi-square.

On our real data the invalid test reports p = 0.047, I² = 24% — a publishable-
looking individual-response finding. The bootstrap-calibrated p-value is
**0.936**.

Individual-response claims are currently fashionable in applied sport science
and are frequently made at exactly these sample sizes. This is a cheap,
demonstrable, and directly useful correction. Implementation and calibration
evidence are in `src/research/simulate_power.py` and
`docs/practice_load_heterogeneity_design.md`.

## Honest positioning

CMJ reliability and SWC work exists in the literature; this is not a new
method. What is defensible as novel here is the scale (5,930 retest pairs per
metric), the D1 football population, the head-to-head ranking of ten metrics
under one consistent protocol, and — most of all — the demonstration that the
standard individual-response test is invalid at the sample sizes the field
actually uses.
