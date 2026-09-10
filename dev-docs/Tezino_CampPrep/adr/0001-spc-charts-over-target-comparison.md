# 0001 — SPC control charts instead of plan-comparison for the 2026 live monitor

Date: 2026-06-09
Status: accepted

## Context

The prescriptive layer needs a reference to judge Tezino's 2026 summer ramp against.
A written return-to-performance progression from sports med / S&C is not accessible to
this project, so "deviation from plan" cannot be the reference. His own 2024/2025 summer
history cannot be the target either: both summers ended in a mid-July injury (2024-07-10
5th MT fracture, 2025-07-10 hip strain), so "tracking with history" is a warning, not a goal.

## Decision

Use statistical process control (XmR individuals charts) as the monitoring frame. In the
staff-facing product, call these **process behavior charts** in the Mark Graban / Donald
J. Wheeler sense: a shared visual method for separating routine noise from meaningful
process signals.

- **Control limits from a healthy, stable baseline window** (post-surgical spring 2026 /
  early June 2026), so the chart detects "his current process is changing" — not
  "he differs from his injured past."
- **Historical pre-injury exposure zones (2024, 2025) drawn as shaded warning bands**,
  not as control limits.
- **Process variables are ramp rates, not raw loads**, for exposure metrics (week-over-week
  change, load vs rolling 28-day average) — raw summer load is intentionally non-stationary
  and would flag the planned progression itself. Response metrics (CMJ mRSI, asymmetry,
  body weight) are charted directly; readiness should be a stable process.
- **Small chart panel** split into exposure (inputs) and response (outputs) to control
  false-alarm inflation.
- **Signal rules matter.** The first technical rule is one point outside the natural
  process limits, where limits are calculated from moving ranges. The live dashboard
  should also support sustained-shift, sustained-trend, and moving-range rules before
  staff-facing launch. See `docs/PROCESS-BEHAVIOR-CHARTS.md`.

## Validation policy (the key trade-off)

The method is validated retrospectively: rebuild the charts on 2024 and 2025 data and check
whether out-of-control signals preceded the two July 10th injuries. **The validation does NOT
gate the live tool — both are built regardless, and the validation result is reported honestly
on the live artifact** ("this method did / did not flag the 2024 fracture in advance").
Process-change detection is valuable even if injury prediction fails.

## Consequences

- Every chart is explainable to staff: average, natural process limits, today's dot, and
  the specific signal rule if one is present. No composite scores.
- If validation fails, the tool's claim weakens from "early warning" to "change detection" —
  and the artifact must say so explicitly.
- Baseline window choice becomes a load-bearing analytical decision (documented when made).
