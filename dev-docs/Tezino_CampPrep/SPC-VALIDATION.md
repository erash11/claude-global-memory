# SPC / Process Behavior Chart Validation Summary

Built 2026-06-11 from `scripts/build_spc_validation.py`.

## Baseline choice

This retrospective validation uses the 2023 healthy summer ramp as the baseline for XmR
limits. This is validation-only. The live 2026 monitor still needs a healthy 2026 baseline
window once surgery/clearance and summer participation are confirmed.

Terminology note: staff-facing artifacts should use **process behavior chart** language
from Mark Graban and Donald J. Wheeler. The limits are natural process limits estimated
from moving ranges, not generic mean plus/minus three sample standard deviations. See
`docs/PROCESS-BEHAVIOR-CHARTS.md`.

## Outputs

- `data/spc_validation/spc_points.csv` — point-level XmR scoring for 2024/2025 using 2023
  limits.
- `data/spc_validation/spc_validation_summary.csv` — one row per ramp and series, with
  pre-injury signal status and lead days.
- `data/spc_validation/spc_validation_notes.md` — generated plain-language notes.

## Result

The validation supports **change detection**, not a strong injury-prediction claim.

- 54 ramp-series summaries were evaluated.
- 11 series had an early-warning signal before the relevant July-10 injury.
- 0 series first signaled only on injury day.
- 43 series had no pre-injury signal.

By ramp:

- 2024: 2 early-warning series, 25 no-preinjury-signal series.
- 2025: 9 early-warning series, 18 no-preinjury-signal series.

Earliest flagged series:

- 2024: CMJ asymmetry signaled 33 days before the foot fracture; GPS total-distance
  vs-28-day-average signaled 19 days before.
- 2025: several GPS rate/proxy series signaled 27 days before; Perch axial vs-28-day
  average series signaled 7 days before; body weight signaled 17 days before; CMJ
  asymmetry signaled 31 days before.

## Interpretation caveats

- This does not prove injury prediction. It shows some process changes were detectable
  before the injuries under a 2023-baselined XmR frame.
- Current validation includes outside-limit, sustained-shift, sustained-trend, and
  moving-range signal rules. The live dashboard should display which rule triggered
  each signal rather than presenting a generic alert.
- Catapult tier-2 rows that use `impacts_high` and `total_high_ima_avg` remain proxies
  until DL-specific acceleration and HSR thresholds are locked.
- Some low-variance 2023 baseline series produce narrow or degenerate XmR limits. Those
  signals should be reviewed as change-detection prompts, not automatic clinical alarms.
