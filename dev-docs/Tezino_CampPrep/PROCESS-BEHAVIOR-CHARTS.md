# Process Behavior Chart Method

This project uses **process behavior charts** as the staff-facing language for SPC.
That follows Mark Graban's framing in *Measures of Success*, which builds on Donald J.
Wheeler's process behavior chart / XmR teaching: the goal is to separate routine noise
from meaningful process signals so staff can react less, lead better, and improve the
system instead of explaining every up/down point.

## Why This Matters Here

The live Tezino monitor should not become another red/yellow/green scoreboard that
pressures staff to explain every fluctuation. A point moving up or down is not
automatically actionable. The chart has to answer:

1. Is this routine variation in the current process?
2. Is this a signal that the process changed?
3. If it is routine variation, what system-level improvement would move the process?

That distinction is the core reason for using process behavior charts instead of
plan-comparison or target-chasing.

## Limit Calculation

For the 2026 live monitor, the selected baseline window is the first four weeks of June
2026 (`2026-06-01` through `2026-06-28`). Review after the first three weeks, then finalize
limits after week four if the window is clinically and operationally acceptable. Until
then, any displayed 2026 live limits are provisional.

For an individuals / moving-range chart, limits are not generic sample-standard-deviation
bands. They are natural process limits estimated from point-to-point movement:

```text
MR_i = abs(X_i - X_{i-1})
MRbar = average(MR_i)
Sigma_estimate = MRbar / 1.128

Center = average(X)
UNPL = Center + 3 * Sigma_estimate
LNPL = Center - 3 * Sigma_estimate
```

Use the staff-facing labels **upper natural process limit** and **lower natural process
limit** where possible. "Control limit" is acceptable in technical notes, but the
dashboard should make clear these are behavior limits, not target thresholds or clinical
cutoffs.

## Signal Rules

The core validation engine implements these rules. The live dashboard should display the
specific rule behind any signal:

- **Rule 1: outside limits** - one point above the upper natural process limit or below
  the lower natural process limit.
- **Rule 2: sustained shift** - eight consecutive points on the same side of the center
  line.
- **Rule 3: sustained trend** - six consecutive points all increasing or all decreasing.
- **Rule 4: moving-range signal** - one moving range above the upper range limit.

Near-limit probability-zone rules can be added later, but should not be the default for
athlete monitoring until false-alarm burden is understood.

## Interpretation Rules

- Do not explain noise. If no process signal is present, avoid assigning a root cause to
  a single high/low point.
- Do explain signals. If a signal appears, ask what changed in training, availability,
  recovery, measurement conditions, or athlete status.
- Do not call natural process limits "safe limits." They describe expected process
  behavior, not injury risk boundaries.
- Do not use 2024/2025 injury history as the target. Historical pre-injury exposure zones
  are warning bands only.
- Use process behavior charts to support staff judgment. They are not clinical diagnosis
  or injury prediction.

## Application To Tezino

- Exposure metrics should be charted as process variables such as week-over-week change
  and current load vs 28-day average, because raw summer load is intentionally ramping.
- Response metrics such as CMJ mRSI, CMJ asymmetry, IMTP PVF/BM, and body weight can be
  charted directly because a stable readiness process is expected.
- The dashboard should explicitly separate **signals** from **context**:
  - Signal: process behavior rule violation.
  - Context: historical warning band, July-10 injury anchor, missing GPS, current clearance
    status, or staff-entered note.

## Sources

- Mark Graban, *Measures of Success: React Less, Lead Better, Improve More*.
- Donald J. Wheeler, *Understanding Variation: The Key to Managing Chaos*.
- Walter A. Shewhart, process-control foundation for common-cause vs special-cause
  variation.
