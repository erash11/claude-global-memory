# Pulse Check PBC Dashboard Design

Date: 2026-06-12
Project: Devonte Tezino Camp Prep

## Decision

Use Option A, **Pulse Check First**, as the next staff-facing dashboard shape.

The dashboard must stop leading with a project/narrative summary and instead behave like
an early-morning process behavior chart monitor. The first screen must answer:

1. Where is he now?
2. What changed?
3. Is the change routine variation or a process signal?
4. Which chart, if any, needs staff discussion?

## Audience And Use Case

Primary users are athletic training and strength staff opening the dashboard early in the
morning for a quick pulse check. They need a compact view of current training activity,
readiness response, trend direction, and signal status.

The dashboard is not a diagnosis tool, a prediction model, or a safe-limit scoreboard.
It supports staff judgment by separating routine noise from process signals.

## Core Layout

The first viewport must use this structure:

1. **Status strip**
   - Generated date and source freshness.
   - Current guardrail mode: historical guardrails or 2026 provisional limits.
   - Count of open process signals.
   - Latest available dates for GPS, Perch, CMJ, and IMTP.

2. **Selected process behavior charts**
   - Average player load per session.
   - High IMA average or high impacts, depending on the cleanest Catapult metric available.
   - Perch axial tonnage.
   - Perch heavy axial reps.
   - CMJ mRSI.
   - CMJ asymmetry.
   - IMTP PVF/BM.

3. **Signal summary**
   - Metrics with a current signal.
   - Rule triggered: outside limits, sustained shift, sustained trend, or moving-range signal.
   - Plain-language discussion prompt.

4. **Secondary context below the fold**
   - Historical 2024/2025 warning context only where it explains why a guardrail exists.
   - SPC validation counts.
   - Caveats and data gaps.

## Metric Selection

Initial selected metrics:

- GPS: average player load per session.
- GPS: high IMA average or high impacts. Prefer the metric with cleaner current extraction and staff interpretability.
- Perch: axial tonnage.
- Perch: axial reps at or above 80 percent.
- CMJ: mRSI.
- CMJ: asymmetry percent.
- IMTP: Peak Vertical Force / BM.

Total distance must not be a primary metric because much of the training is indoors and
distance can understate actual training stress.

Acute:chronic and other ratio-style workload panels are explicitly out of the first rebuild.
They can become a future adjunct view after the core process monitor works.

## Guardrail Strategy

Use a hybrid guardrail rule:

- Start each metric with historical guardrails.
- Label these explicitly as **historical guardrails**, not 2026 limits.
- Switch a metric to **2026 provisional process limits** only after that metric has enough current observations.
- Minimum current observations:
  - GPS and Perch session metrics: 5 current training sessions.
  - CMJ and IMTP response metrics: 5 current tests.
- The first four weeks of June 2026 remain the preferred baseline window for final 2026 limits.
- Until the baseline window is complete and accepted, 2026 limits are provisional.

This avoids two failure modes:

- Over-trusting historical injury-ramp context as if it were a safe threshold.
- Over-trusting sparse 2026 data as if it were a stable current process.

## Process Behavior Chart Requirements

Each chart must show:

- Current 2026 points.
- Center line.
- Upper natural process limit.
- Lower natural process limit where meaningful.
- Guardrail source label.
- Latest point value and date.
- Signal state.
- Triggered rule if a signal exists.

For metrics where lower limits are not meaningful for staff interpretation, the chart may
still compute a lower natural process limit but must visually emphasize the relevant
direction of concern.

The chart language must use:

- "Upper natural process limit"
- "Lower natural process limit"
- "Routine variation"
- "Process signal"
- "Historical guardrail"
- "2026 provisional limit"

Avoid:

- "Safe limit"
- "Injury prediction"
- "Risk score"
- "Target"

## Data Contract Changes

Add a top-level `pulse_monitor` object to `data/dashboard/dashboard_data.json`.

Expected shape:

```json
{
  "pulse_monitor": {
    "guardrail_policy": {},
    "source_freshness": [],
    "status": {},
    "metrics": [],
    "signals": []
  }
}
```

Each metric entry must include:

- `id`
- `label`
- `domain`
- `source`
- `unit`
- `points`
- `center`
- `unpl`
- `lnpl`
- `guardrail_source`
- `minimum_current_observations`
- `current_observations`
- `latest_point`
- `signal_state`
- `signal_rule`
- `staff_prompt`

Existing `current_ramp`, `current_forceplate`, `live_baseline`, and historical sections can
remain in the contract during the transition, but the HTML must lead with `pulse_monitor`.

## HTML Requirements

The static HTML must lead with:

- Title: "Tezino Morning Pulse Check"
- Subtitle: "Selected process behavior charts for current summer ramp monitoring."
- Compact status strip.
- Chart grid of selected PBC panels.
- Signal summary.

Historical warning references must move below the fold or into a collapsed secondary
section. They must not dominate the first screen.

The first pass can use inline SVG charts generated in the existing static page, with no
new frontend framework.

## Testing Requirements

Add or update tests to prove:

- `pulse_monitor` exists in the JSON contract.
- Average player load per session is included instead of total distance as a primary metric.
- The hybrid guardrail policy is represented in the payload.
- Metrics with fewer than 5 current observations stay on historical guardrails.
- Metrics with at least 5 current observations can use 2026 provisional limits.
- The HTML contains "Tezino Morning Pulse Check".
- The HTML renders selected PBC chart containers.
- The HTML does not lead with 2024/2025 warning reference cards.

## Non-Goals

- Do not add scheduling or automation yet.
- Do not build acute:chronic workload panels in this pass.
- Do not turn historical warning bands into safe thresholds.
- Do not introduce a React or server app.
- Do not remove the existing generated data chain unless a schema change requires it.

## Implementation Order

1. Add tests for the `pulse_monitor` JSON contract.
2. Build pulse metric selection and guardrail policy in `scripts/build_dashboard_data.py`.
3. Add tests for the new HTML lead section.
4. Rework `scripts/build_dashboard_html.py` so Option A leads the page.
5. Refresh generated dashboard artifacts.
6. Run the full test suite and inspect the static dashboard.
